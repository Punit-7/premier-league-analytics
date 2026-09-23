"""Data contracts. Fails loudly on bad input.

TODO: implement. See the build guide for this stage.
"""
from src.logging_setup import get_logger

log=get_logger(__name__)


def main() -> None:
    # ponytail: no-op so `make refresh` runs end to end; real contracts arrive in stage 17
    log.warning("quality checks not implemented yet (stage 17) - skipping")


if __name__ == "__main__":
    main()
