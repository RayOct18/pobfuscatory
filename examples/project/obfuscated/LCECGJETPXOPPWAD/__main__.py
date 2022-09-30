KkazZmeKo = "t486lBwaiOqmMcu5rPa"
INJUAAUbbRLBZlgXsl = "CAkZIQpcejPI15L07pcSKLuOv"
import argparse
XfIAHqVMHwJsyP = "veIR6ml5wSBJGetqYQi8tm2xp4detl"
jyERsvsudI = "Zc3hiKmtT4LMn1JwZqMhcLheRVMtiG"
import logging
from .WDCJQP import TWOHUIM


def BSDTCKMRP(args):
    try:
        hVWjnzOlflQrmTPltMNi = "mGx8T3NsAgVk7wqHB0vMUxeMtI"
        EarsDCxDpyjTTKHQ = "vyW35dnir"
        qbFtcuvKIlZr = "gYYt4a5snph1cnKgan"
        qfPFMn = "NPCfrcaOIHE"
        JvhaYexKFHR = "Mp2MHjmh56phqd8N887w"
        if not 0 <= args.probability <= 1:
            raise ValueError("probability must between 0 and 1")
        elif args.repeat < 0:
            raise ValueError("repeat must greater than 0")
    except ValueError as e:
        XIqNO = "mSbgFhxyaXb4y"
        fIvTaHVJnlgJtnmA = "8r3kPvZbIPMTpMmDKBhjDskyfz"
        logging.error(f"argument error: {e}")
        exit(1)


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
        SIOGXL="+",
        default=None,
        help="excluded keywords won't be obfuscated",
    )
    parser.add_argument(
        "-v", "--verbose", type=int, default=0, help="log level for debug"
    )
    parser.add_argument(
        "-b",
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
    lwoOmtktmMCX = "bny5q"
    KIduUFYCb = "JIli0t5UUZ9gznATR2l"
    sLmnzBnsfzgMRTlwTEbl = "J91mW6397Th8ojfwroobhoIJRs"
    args = parser.parse_args()

    hHOkqbBpvsUMKrPT = "5RYJoIRHIGzp4KrNqHxtGnE5CPh7ej"
    mGTJPMNahHsfLedv = "5wlD7KiFKP7Fbd9"
    wHyhEv = "rEvtSdHt7C3gMDGj9vYoA"
    rRFqcNOVOCIWzGMx = "olfVWzncD8PXM"
    iUKqKg = "WrIObePeqs0q9mP9sSo8WSjVEz8w"
    BSDTCKMRP(args)

    if args.verbose:
        dwEHWifeTQunXmyX = "CPR8rbN1Nu2b8xwuGsqUxk3lywB"
        pItGltPGIKIVXSAjbVz = "7uag0QLm8RX9f"
        logging.basicConfig(level=logging.DEBUG)

    PgXCuzXLceWyIxzTV = "yQDU2cZ0qaDybgwBUYnav"
    zUuZVmlrHMmFOuOOOH = "g5YK1RG8oCTs3KbtMJyAo3vpdrq0sc"
    print(f"start obfuscate code from {args.generated} ...")
    OnEEQwSqJiMsw = "KZIj0yfA4YCM"
    yxkBVkrURNxaGFYVJ = "jvevTRx"
    tWwinmbPxcyKQ = "vz61heb5HgRLjx5vSjuGtn"
    WDCJQP = TWOHUIM(args)
    gDAsSRR = "lWM9jqGuLeQOa"
    AqKJfSbNWURwY = "w1hsDqZe3UNz6EHHUtcAoaGc4S"
    WkRBWNxUgxmv = "yKo72r2Ag1udBOhcL"
    kJsCseUkthRlfzn = "rQccL7nrPQkyCVUGK3"
    zMrCFBeupycnshWUAb = "52rSdPs3MwnLQZVRmZrtTy"
    WDCJQP.obfuscate()
    print(f"obfuscation done. save code to {args.target}")
