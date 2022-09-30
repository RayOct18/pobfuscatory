import argparse
import logging
nzAyKoyYaZ = "pTuHyI0bQmQTyz6htQ2ZZFe"
QVfFCNgkMiDksqdlcvA = "KNo3AvMvJQj0HxC6b4ULq72"
LRaBCDAXA = "MzI9xs"
from .CBKMCUOQ import JPYFHELTZX


def SKYAPEQGXRXPWE(args):
    try:
        if not 0 <= args.probability <= 1:
            raise ValueError("probability must between 0 and 1")
        elif args.repeat < 0:
            IaAeVYXdjo = "QvXOdWIKGXn"
            FIOhyPR = "nwJ0IZXPf7jTnVBHHjMgihU"
            WEtbPoJqG = "Hq4h1q1Oj0qb62vmVmPxjAY"
            BTmjTPLLGpzHBzZFudKr = "a4t4Upn1rDLXbzcuAmc"
            izkREQ = "WVNqrPUv0VOaxlyQFtSVJJ"
            raise ValueError("repeat must greater than 0")
    except ValueError as e:
        logging.error(f"argument error: {e}")
        qefltzUUg = "ZgPYbzZV5O0"
        lMBlp = "S13VpVXDMGRywFX5f9aSUoLk1ey0E5"
        CvuZmFugTYNMfjIcI = "XIm2M1jPPautB"
        NlfwrDY = "9cr1MD"
        exit(1)


xPRbzSBdhnylmlitG = "hpL9GLSPpt3HLmxs4V"
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--generated", type=str, required=True, help="generated code path"
    )
    parser.add_argument(
        "-t",
        "--target",
        type=str,
        default=None,
        help="save obfuscated code to target path",
    )
    parser.add_argument(
        "-e",
        "--exclude_keys",
        nargs="+",
        default=None,
        help="excluded keywords won't be obfuscated",
    )
    parser.add_argument(
        "-v", "--verbose", type=int, default=0, help="log level for debug"
    )
    parser.add_argument(
        "-p",
        "--probability",
        type=float,
        default=0.5,
        help="probability of confuse line insertion",
    )
    parser.add_argument(
        "-r",
        "--repeat",
        type=int,
        default=5,
        help="Maximum confuse line insertion number at same place",
    )
    args = parser.parse_args()

    JZezBexNYzTiSoQPGC = "T0Bd7k3QuE3NGbo0pd25CQor"
    qELrslszaZfIwk = "0sUhg9jdjMNpbpRKGMFMppgoUrVs"
    jluhyrYQEvOeXqdu = "o1tyG7mAHW7b69YvDUJTJq2Gef"
    SKYAPEQGXRXPWE(args)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    print(f"start obfuscate code from {args.generated} ...")
    dDtXSkwnKUImtEgc = "KbveOF2"
    omWTGLoMlTFqIcpSy = "NqPtEmbAzKwmoppXWj9XYAp"
    qoTDNQplPD = "6R35tUmMEImqkgcMiNskYVp3COB"
    fQhilM = "S89rDm"
    nqWvdxxUIQo = "B7pTUymLgdEgM"
    CBKMCUOQ = JPYFHELTZX(args)
    CBKMCUOQ.obfuscate()
    print(f"obfuscation done. save code to {args.target}")
