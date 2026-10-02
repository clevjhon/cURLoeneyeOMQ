#include <stdlib.h>
typedef struct IRNode { int op; int reg; struct IRNode *next; } IRNode;
#define OP_STORE 1
#define OP_LOAD 2
void oeneye_optimize_ir(IRNode *node) {
    while (node != NULL) {
        if (node->op == OP_STORE && node->next && node->next->op == OP_LOAD) {
            if (node->reg == node->next->reg) {
                IRNode *obsolete = node->next;
                node->next = obsolete->next;
                free(obsolete);
            }
        }
        node = node->next;
    }
}
