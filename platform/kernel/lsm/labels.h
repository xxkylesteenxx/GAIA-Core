/* GAIA LSM security label definitions
 *
 * Labels are stored as xattrs on filesystem objects:
 *   setfattr -n security.gaia -v gaia.actuation /path/to/actuator
 *
 * Kernel LSM and userspace policy engine share this header.
 */
#pragma once

/* Core identity label — marks GAIA core process binaries */
#define GAIA_LABEL_CORE       "gaia.core"

/* Safety boundary label — marks safety-critical paths and FDs */
#define GAIA_LABEL_SAFETY     "gaia.safety"

/* Actuation label — marks paths that trigger physical actuation */
#define GAIA_LABEL_ACTUATION  "gaia.actuation"

/* Risk label — marks elevated-risk actuation resources */
#define GAIA_LABEL_RISK       "gaia.risk"

/* Clearance label — marks pre-approved actuation tokens */
#define GAIA_LABEL_CLEARANCE  "gaia.clearance"
