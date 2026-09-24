# PlatformIO pre-script: stamp the firmware with the Git commit (logged by TBK-TST-001).
# Licensed MIT (see LICENSE-SOFTWARE).
import subprocess

Import("env")  # noqa: F821  (provided by PlatformIO)


def rev():
    try:
        r = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
        dirty = subprocess.call(["git", "diff", "--quiet", "HEAD", "--", "."]) != 0
        return r + ("-dirty" if dirty else "")
    except Exception:
        return "unknown"


env.Append(CPPDEFINES=[("TB_FW_REV", '\\"%s\\"' % rev())])  # noqa: F821
