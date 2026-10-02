//
//  OeneyeClock.m
//  Objective-C port of the Python OeneyeRuntimeKernel class.
//
//  This is a literal translation of the original's math: a 2x2 covariance
//  matrix scaled by (inertiaMoment / jdCube), then used to compute a
//  Mahalanobis distance between a fixed sample point and mu = [22/7, pi].
//  The 2x2 matrix inverse is done by the closed-form formula (no external
//  linear-algebra dependency needed for a 2x2). The "secure mount" fields
//  in the returned dictionary are, as in the original, just descriptive
//  strings -- no actual mounting/file I/O happens here or in the source.
//
//  Build:  clang -fobjc-arc -framework Foundation OeneyeClock.m -o oeneyeclock
//  Run:    ./oeneyeclock
//

#import <Foundation/Foundation.h>
#import <math.h>

@interface OeneyeRuntimeKernel : NSObject

@property (nonatomic, readonly) double inertiaMomentMM4;
@property (nonatomic, readonly) double jdCube;
@property (nonatomic, readonly) double mu0;   // mu[0] = 22/7
@property (nonatomic, readonly) double mu1;   // mu[1] = pi
@property (nonatomic, readonly) double delta; // |pi - 22/7|

- (instancetype)initWithInertiaMomentMM4:(double)inertiaMomentMM4
                                   jdCube:(double)jdCube;

/// Scales a 2x2 base covariance matrix by (I / jd^3).
/// baseSigma / outSigma are 4-element arrays in row-major order: [a00, a01, a10, a11].
- (void)computeModifiedCovariance:(const double[4])baseSigma
                            output:(double[4])outSigma;

/// Mahalanobis distance^2 between 2-vector x and mu, using the modified covariance.
- (double)mahalanobisInertiaDistanceSquared:(const double[2])x
                                  baseSigma:(const double[4])baseSigma;

/// Equivalent of execute_borophene_pipeline(record_pointer) -> dict
- (NSDictionary<NSString *, id> *)executeBorophenePipeline:(NSString *)recordPointer;

@end


@implementation OeneyeRuntimeKernel

- (instancetype)initWithInertiaMomentMM4:(double)inertiaMomentMM4
                                   jdCube:(double)jdCube {
    self = [super init];
    if (self) {
        _inertiaMomentMM4 = inertiaMomentMM4;
        _jdCube = jdCube;
        _mu0 = 22.0 / 7.0;
        _mu1 = M_PI;
        _delta = fabs(M_PI - (22.0 / 7.0));
    }
    return self;
}

- (void)computeModifiedCovariance:(const double[4])baseSigma
                            output:(double[4])outSigma {
    double scalingFactor = self.inertiaMomentMM4 / self.jdCube;
    for (int i = 0; i < 4; i++) {
        outSigma[i] = baseSigma[i] * scalingFactor;
    }
}

/// Closed-form inverse of a 2x2 matrix [[a,b],[c,d]]:
///   inv = 1/det * [[d,-b],[-c,a]],  det = ad - bc
static BOOL invert2x2(const double m[4], double outInv[4]) {
    double a = m[0], b = m[1], c = m[2], d = m[3];
    double det = a * d - b * c;
    if (det == 0.0) return NO;
    double invDet = 1.0 / det;
    outInv[0] =  d * invDet;
    outInv[1] = -b * invDet;
    outInv[2] = -c * invDet;
    outInv[3] =  a * invDet;
    return YES;
}

- (double)mahalanobisInertiaDistanceSquared:(const double[2])x
                                  baseSigma:(const double[4])baseSigma {
    double tildeSigma[4];
    [self computeModifiedCovariance:baseSigma output:tildeSigma];

    double invSigma[4];
    if (!invert2x2(tildeSigma, invSigma)) {
        [NSException raise:@"SingularMatrixException"
                     format:@"modified covariance matrix is not invertible"];
    }

    double diff[2] = { x[0] - self.mu0, x[1] - self.mu1 };

    // tmp = invSigma * diff
    double tmp[2] = {
        invSigma[0] * diff[0] + invSigma[1] * diff[1],
        invSigma[2] * diff[0] + invSigma[3] * diff[1],
    };
    // d^2 = diff . tmp
    double dSquared = diff[0] * tmp[0] + diff[1] * tmp[1];
    return dSquared;
}

- (NSDictionary<NSString *, id> *)executeBorophenePipeline:(NSString *)recordPointer {
    // Secure mount handling for 5.5 TB Borophene record
    double baseSigma[4] = {
        1.0,  0.05,
        0.05, 1.0 + self.delta * self.delta
    };
    double sampleState[2] = { 3.14159, 3.14159 };

    double d2 = [self mahalanobisInertiaDistanceSquared:sampleState baseSigma:baseSigma];

    return @{
        @"status": @"SECURE_MOUNT_ACTIVE",
        @"target_record": recordPointer ?: [NSNull null],
        @"inertia_distance_squared": @(d2),
    };
}

@end


int main(int argc, const char * argv[]) {
    @autoreleasepool {
        OeneyeRuntimeKernel *kernel =
            [[OeneyeRuntimeKernel alloc] initWithInertiaMomentMM4:1420.5 jdCube:12.0];

        NSDictionary *result =
            [kernel executeBorophenePipeline:@"/mnt/borophene_5_5tb/core.dat"];

        NSLog(@"Kernel Execution Result: %@", result);
    }
    return 0;
}
