/*
 * oeneyepdf.c - oeneyePDF reference writer, spec v0.1 (milestone M1)
 *
 * Plain text -> PDF 1.4, standard-14 fonts only, streaming output.
 * Portable C89: builds with gcc, Open Watcom (16-bit small model) and
 * Turbo C. This is the reference for the later 16-bit assembly port.
 *
 * Usage:  OENEYEPDF in.txt out.pdf [/A4|/LETTER] [/MONO]
 *                   [/CP850|/CP437|/UTF8] [/BRAND]
 *
 * Markup: "# " "## " "### " headings, blank line = paragraph break,
 *         ``` toggles a Courier block, everything else is wrapped body.
 *
 * Object layout:
 *   1 Catalog   2 Pages   3 F1 Helvetica   4 F2 Courier
 *   5 F3 Symbol 6 F4 Helvetica-Bold        7 Info
 *   8.. per page: Page, Contents, Length (3 objects)
 * Pages (obj 2), Info (7) and Catalog (1) are written last, so no page
 * is ever buffered. Contents use an indirect /Length object.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXOBJ   4000       /* 4 bytes per entry = 16 KB on DOS       */
#define FIRSTPG  8
#define LINEMAX  1024
#define BUFMAX   1100
#define INF      0x81       /* internal marker for U+221E (infinity)  */
#define MARGIN   56
#define BOTTOM   64
#define GAP      6

/* Helvetica advance widths, 1/1000 em, chars 32..126 */
static const int helv[95] = {
    278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556,
   1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
    333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
    556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584
};

/* CP850 0x80..0xFF -> WinAnsi byte (box drawing folded to + - | #) */
static const unsigned char cp850[128] = {
    0xC7,0xFC,0xE9,0xE2,0xE4,0xE0,0xE5,0xE7,0xEA,0xEB,0xE8,0xEF,0xEE,0xEC,0xC4,0xC5,
    0xC9,0xE6,0xC6,0xF4,0xF6,0xF2,0xFB,0xF9,0xFF,0xD6,0xDC,0xF8,0xA3,0xD8,0xD7,0x83,
    0xE1,0xED,0xF3,0xFA,0xF1,0xD1,0xAA,0xBA,0xBF,0xAE,0xAC,0xBD,0xBC,0xA1,0xAB,0xBB,
    0x23,0x23,0x23,0x7C,0x7C,0xC1,0xC2,0xC0,0xA9,0x7C,0x7C,0x2B,0x2B,0xA2,0xA5,0x2B,
    0x2B,0x2B,0x2B,0x2B,0x2D,0x2B,0xE3,0xC3,0x2B,0x2B,0x2B,0x2B,0x7C,0x3D,0x2B,0xA4,
    0xF0,0xD0,0xCA,0xCB,0xC8,0x69,0xCD,0xCE,0xCF,0x2B,0x2B,0x23,0x23,0xA6,0xCC,0x23,
    0xD3,0xDF,0xD4,0xD2,0xF5,0xD5,0xB5,0xFE,0xDE,0xDA,0xDB,0xD9,0xFD,0xDD,0xAF,0xB4,
    0xAD,0xB1,0x3D,0xBE,0xB6,0xA7,0xF7,0xB8,0xB0,0xA8,0xB7,0xB9,0xB3,0xB2,0x23,0xA0
};

static FILE *out;
static const char *outname = NULL;
static unsigned long pos = 0UL;
static unsigned long offs[MAXOBJ + 1];
static unsigned long cstart;

static int PW = 595, PH = 842;
static int npages = 0, page_open = 0, y = 0;
static int brand = 0, monodoc = 0, codepage = 850;   /* 0 = UTF-8 */
static char title[81];

/* current text style */
static int fontid = 1, fsize = 11, flead = 14;
static long cap;                        /* line capacity, 1/1000 em */

/* line and word buffers */
static unsigned char wl[BUFMAX];  static int wln = 0;  static long wlw = 0L;
static unsigned char wd[BUFMAX];  static int wdn = 0;  static long wdw = 0L;
static int para_open = 0;

static void die(const char *msg)
{
    fprintf(stderr, "OENEYEPDF: %s\n", msg);
    if (out != NULL) { fclose(out); out = NULL; if (outname) remove(outname); }
    exit(2);
}

static void wrc(int c)
{
    if (putc(c, out) == EOF) die("write error");
    pos++;
}

static void wr(const char *s)
{
    while (*s) wrc((unsigned char)*s++);
}

static void esc(int c)
{
    char t[8];
    if (c == '(' || c == ')' || c == '\\') { wrc('\\'); wrc(c); }
    else if (c < 32 || c > 126) { sprintf(t, "\\%03o", c); wr(t); }
    else wrc(c);
}

static void obj(int n)
{
    char t[24];
    if (n > MAXOBJ) die("too many objects");
    offs[n] = pos;
    sprintf(t, "%d 0 obj\n", n);
    wr(t);
}

/* ---- metrics ------------------------------------------------------ */

static long cw(int c)
{
    long w;
    if (fontid == 2) return 600L;
    if (c == INF) return 713L;
    if (c >= 32 && c <= 126) w = helv[c - 32];
    else switch (c) {
        case 0xC4: w = 667; break;   /* A umlaut */
        case 0xD6: w = 778; break;   /* O umlaut */
        case 0xDC: w = 722; break;   /* U umlaut */
        case 0xDF: w = 611; break;   /* sharp s  */
        case 0x85: case 0x97: w = 1000; break;
        case 0x91: case 0x92: w = 222; break;
        case 0x93: case 0x94: w = 333; break;
        case 0x95: w = 350; break;
        default:
            w = (c >= 0xC0 && c <= 0xDE && c != 0xD7) ? 722 : 556;
    }
    if (fontid == 4) w += w / 10;        /* bold: conservative estimate */
    return w;
}

static void set_style(int font, int size, int lead)
{
    fontid = font; fsize = size; flead = lead;
    cap = (long)(PW - 2 * MARGIN) * 1000L / size;
}

static void set_body(void)
{
    if (monodoc) set_style(2, 10, 12); else set_style(1, 11, 14);
}

/* ---- pages -------------------------------------------------------- */

static void emit_line(const unsigned char *s, int n, int font, int size,
                      int x, int yb)
{
    char t[80];
    int i;
    sprintf(t, "BT /F%d %d Tf %d %d Td (", font, size, x, yb);
    wr(t);
    for (i = 0; i < n; i++) {
        if (s[i] == INF) {
            sprintf(t, ") Tj /F3 %d Tf (\\245) Tj /F%d %d Tf (", size, font, size);
            wr(t);
        } else esc(s[i]);
    }
    wr(") Tj ET\n");
}

static void begin_page(void)
{
    char t[300];
    int p, c;
    if (FIRSTPG + 3 * npages + 2 > MAXOBJ) die("too many pages");
    p = FIRSTPG + 3 * npages;
    c = p + 1;
    npages++;
    obj(p);
    sprintf(t, "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] "
               "/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R "
               "/F4 6 0 R >> >> /Contents %d 0 R >>\nendobj\n", PW, PH, c);
    wr(t);
    obj(c);
    sprintf(t, "<< /Length %d 0 R >>\nstream\n", c + 1);
    wr(t);
    cstart = pos;
    page_open = 1;
    y = PH - MARGIN;
}

static void end_page(void)
{
    char t[24];
    unsigned char tok[3];
    unsigned long clen;
    int n, p;

    n = sprintf(t, "- %d -", npages);
    emit_line((unsigned char *)t, n, 1, 9, PW / 2 - n * 3, 30);
    if (brand) {
        tok[0] = '0'; tok[1] = INF; tok[2] = ';';
        emit_line(tok, 3, 1, 9, MARGIN, 30);
    }
    clen = pos - cstart;
    wr("\nendstream\nendobj\n");
    p = FIRSTPG + 3 * (npages - 1) + 2;
    obj(p);
    sprintf(t, "%lu\nendobj\n", clen);
    wr(t);
    page_open = 0;
}

static void newpage(void)
{
    if (page_open) end_page();
    begin_page();
}

static void put_line(const unsigned char *s, int n)
{
    if (!page_open || y - flead < BOTTOM) newpage();
    if (n > 0) emit_line(s, n, fontid, fsize, MARGIN, y - fsize);
    y -= flead;
}

/* ---- word wrapping ------------------------------------------------ */

static void flush_line(void)
{
    if (wln > 0) put_line(wl, wln);
    wln = 0; wlw = 0L;
}

static void addc(int c)
{
    if (wln >= BUFMAX - 1) flush_line();
    wl[wln++] = (unsigned char)c;
    wlw += cw(c);
}

static void put_word(void)
{
    int i;
    long sp;
    if (wdn == 0) return;
    para_open = 1;
    sp = cw(' ');
    if (wln > 0 && wlw + sp + wdw > cap) flush_line();
    if (wln > 0) addc(' ');
    if (wlw + wdw <= cap) {
        for (i = 0; i < wdn; i++) addc(wd[i]);
    } else {                            /* word longer than a line */
        for (i = 0; i < wdn; i++) {
            if (wlw + cw(wd[i]) > cap) flush_line();
            addc(wd[i]);
        }
    }
    wdn = 0; wdw = 0L;
}

static void words(const unsigned char *s, int n)
{
    int i;
    for (i = 0; i < n; i++) {
        if (s[i] == ' ') put_word();
        else {
            if (wdn >= BUFMAX - 1) put_word();
            wd[wdn++] = s[i];
            wdw += cw(s[i]);
        }
    }
    put_word();
}

static void end_para(void)
{
    flush_line();
    if (para_open) { y -= GAP; para_open = 0; }
}

static void heading(const unsigned char *s, int n, int lvl)
{
    int i, k;
    end_para();
    if (page_open && y - 8 - 40 < BOTTOM) newpage();
    if (page_open && y < PH - MARGIN) y -= 8;
    if (lvl == 1) set_style(4, 16, 20);
    else if (lvl == 2) set_style(4, 13, 17);
    else set_style(4, 11, 15);
    words(s, n);
    flush_line();
    y -= 4;
    if (title[0] == '\0') {
        for (i = 0, k = 0; i < n && k < 80; i++) {
            if (s[i] >= 32 && s[i] <= 126) title[k++] = (char)s[i];
            else title[k++] = '?';
        }
        title[k] = '\0';
    }
    set_body();
    para_open = 0;
}

static void code_line(const unsigned char *s, int n)
{
    int maxc = (int)(cap / 600L);
    int off = 0;
    if (maxc < 1) maxc = 1;
    if (n == 0) { put_line(s, 0); return; }
    while (off < n) {
        int len = n - off;
        if (len > maxc) len = maxc;
        put_line(s + off, len);
        off += len;
    }
}

/* ---- input decoding ----------------------------------------------- */

static int map437(int c)
{
    switch (c) {
    case 0x9B: return 0xA2;   case 0x9D: return 0xA5;
    case 0x9E: return 'P';    case 0xA9: return '-';
    case 0xB5: case 0xB6: case 0xB7: case 0xB8:
    case 0xBD: case 0xBE: case 0xC6: case 0xC7: case 0xCF:
    case 0xD0: case 0xD1: case 0xD2: case 0xD3: case 0xD4:
    case 0xD5: case 0xD6: case 0xD7: case 0xD8: return '+';
    case 0xDD: case 0xDE: return '#';
    case 0xE0: return 'a';    case 0xE2: return 'G';
    case 0xE3: return 'p';    case 0xE4: return 'S';
    case 0xE5: return 's';    case 0xE6: return 0xB5;
    case 0xE7: return 't';    case 0xE8: return 'F';
    case 0xE9: return 'T';    case 0xEA: return 'O';
    case 0xEB: return 'd';    case 0xEC: return INF;
    case 0xED: return 'f';    case 0xEE: return 'e';
    case 0xEF: return 'n';    case 0xF0: return '=';
    case 0xF2: return '>';    case 0xF3: return '<';
    case 0xF4: case 0xF5: return '|';
    case 0xF6: return 0xF7;   case 0xF7: return '~';
    case 0xF8: return 0xB0;   case 0xF9: case 0xFA: return 0xB7;
    case 0xFB: return 'v';    case 0xFC: return 'n';
    case 0xFD: return 0xB2;   case 0xFE: return '#';
    case 0xFF: return 0xA0;
    default:   return cp850[c - 128];
    }
}

static int uni2ansi(unsigned long u)
{
    if (u >= 0xA0UL && u <= 0xFFUL) return (int)u;
    switch (u) {
    case 0x192:  return 0x83;  case 0x20AC: return 0x80;
    case 0x2013: return 0x96;  case 0x2014: return 0x97;
    case 0x2018: return 0x91;  case 0x2019: return 0x92;
    case 0x201C: return 0x93;  case 0x201D: return 0x94;
    case 0x2022: return 0x95;  case 0x2026: return 0x85;
    case 0x221E: return INF;
    case 0xFEFF: return -1;                     /* BOM: drop */
    default:     return '?';
    }
}

static int decode(const unsigned char *r, int n, unsigned char *d)
{
    int i = 0, k = 0, c, a;
    unsigned long u;
    while (i < n) {
        c = r[i++];
        if (c == '\t') {
            int j;
            for (j = 0; j < 4 && k < LINEMAX; j++) d[k++] = ' ';
            continue;
        }
        if (c < 32 || c == 127) continue;
        if (c < 128) { d[k++] = (unsigned char)c; continue; }
        if (codepage == 0) {
            if ((c & 0xE0) == 0xC0 && i < n) {
                u = ((unsigned long)(c & 0x1F) << 6) | (r[i] & 0x3F);
                i += 1;
            } else if ((c & 0xF0) == 0xE0 && i + 1 < n) {
                u = ((unsigned long)(c & 0x0F) << 12) |
                    ((unsigned long)(r[i] & 0x3F) << 6) | (r[i + 1] & 0x3F);
                i += 2;
            } else if ((c & 0xF8) == 0xF0 && i + 2 < n) {
                u = 0x3F; i += 3;
            } else u = 0x3F;
            a = uni2ansi(u);
        } else if (codepage == 437) a = map437(c);
        else a = cp850[c - 128];
        if (a >= 0) d[k++] = (unsigned char)a;
    }
    return k;
}

/* ---- main --------------------------------------------------------- */

static void process(FILE *in)
{
    char raw[LINEMAX + 2];
    unsigned char dl[LINEMAX + 2];
    int n, i, lvl, incode = 0, eof = 0;
    char *p;

    while (!eof && fgets(raw, sizeof raw, in) != NULL) {
        p = strchr(raw, 0x1A);                  /* DOS Ctrl-Z = EOF */
        if (p != NULL) { *p = '\0'; eof = 1; }
        n = (int)strlen(raw);
        n = decode((unsigned char *)raw, n, dl);

        if (n >= 3 && memcmp(dl, "```", 3) == 0) {
            end_para();
            if (!incode) { incode = 1; set_style(2, 10, 12); }
            else { incode = 0; set_body(); y -= 4; }
            continue;
        }
        if (incode) { code_line(dl, n); continue; }

        i = 0;
        while (i < n && dl[i] == ' ') i++;
        if (i == n) { end_para(); continue; }

        lvl = 0;
        while (lvl < n && dl[lvl] == '#') lvl++;
        if (lvl >= 1 && lvl <= 3 && lvl < n && dl[lvl] == ' ') {
            heading(dl + lvl + 1, n - lvl - 1, lvl);
            continue;
        }
        words(dl + i, n - i);
    }
    end_para();
}

static void upcase(char *s)
{
    for (; *s; s++) if (*s >= 'a' && *s <= 'z') *s = (char)(*s - 32);
}

int main(int argc, char **argv)
{
    FILE *in;
    char opt[16], t[300];
    unsigned long xrefpos;
    int i, size;

    if (argc < 3) {
        fprintf(stderr, "oeneyePDF 0.1\nUsage: OENEYEPDF in.txt out.pdf "
                "[/A4|/LETTER] [/MONO] [/CP850|/CP437|/UTF8] [/BRAND]\n");
        return 1;
    }
    for (i = 3; i < argc; i++) {
        char *a = argv[i];
        if (*a == '/' || *a == '-') a++;
        strncpy(opt, a, sizeof opt - 1); opt[sizeof opt - 1] = '\0';
        upcase(opt);
        if (!strcmp(opt, "A4")) { PW = 595; PH = 842; }
        else if (!strcmp(opt, "LETTER")) { PW = 612; PH = 792; }
        else if (!strcmp(opt, "MONO")) monodoc = 1;
        else if (!strcmp(opt, "CP850")) codepage = 850;
        else if (!strcmp(opt, "CP437")) codepage = 437;
        else if (!strcmp(opt, "UTF8")) codepage = 0;
        else if (!strcmp(opt, "BRAND")) brand = 1;
        else { fprintf(stderr, "OENEYEPDF: unknown option %s\n", argv[i]); return 1; }
    }

    in = fopen(argv[1], "rb");
    if (in == NULL) die("cannot open input");
    out = fopen(argv[2], "wb");
    if (out == NULL) die("cannot create output");
    outname = argv[2];

    title[0] = '\0';
    set_body();

    wr("%PDF-1.4\n%");
    wrc(0xE2); wrc(0xE3); wrc(0xCF); wrc(0xD3);
    wr("\n");

    obj(3); wr("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj\n");
    obj(4); wr("<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>\nendobj\n");
    obj(5); wr("<< /Type /Font /Subtype /Type1 /BaseFont /Symbol >>\nendobj\n");
    obj(6); wr("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>\nendobj\n");

    process(in);
    fclose(in);
    if (npages == 0) newpage();
    if (page_open) end_page();

    obj(2);
    sprintf(t, "<< /Type /Pages /Count %d /Kids [\n", npages);
    wr(t);
    for (i = 0; i < npages; i++) {
        sprintf(t, "%d 0 R%s", FIRSTPG + 3 * i, (i % 8 == 7) ? "\n" : " ");
        wr(t);
    }
    wr("\n] >>\nendobj\n");

    obj(7);
    wr("<< /Title (");
    for (i = 0; title[i]; i++) esc((unsigned char)title[i]);
    if (!title[0]) wr("Untitled");
    wr(") /Producer (oeneyePDF 0.1) >>\nendobj\n");

    obj(1);
    wr("<< /Type /Catalog /Pages 2 0 R >>\nendobj\n");

    xrefpos = pos;
    size = FIRSTPG + 3 * npages;
    sprintf(t, "xref\n0 %d\n", size);
    wr(t);
    wr("0000000000 65535 f \n");
    for (i = 1; i < size; i++) {
        sprintf(t, "%010lu 00000 n \n", offs[i]);
        wr(t);
    }
    sprintf(t, "trailer\n<< /Size %d /Root 1 0 R /Info 7 0 R >>\n"
               "startxref\n%lu\n%%%%EOF\n", size, xrefpos);
    wr(t);

    if (fclose(out) == EOF) die("close error");
    fprintf(stderr, "OENEYEPDF: %d page(s), %lu bytes\n", npages, pos);
    return 0;
}
