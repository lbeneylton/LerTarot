import asyncio
import logging
import sys

from app.modules.emails.worker import email_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


async def main() -> None:
    """Ponto de entrada para executar o Email Worker em um processo isolado."""
    logger = logging.getLogger("emails.cli")
    logger.info("Iniciando Email Worker como um processo dedicado CLI...")
    try:
        await email_worker.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Encerrando Email Worker CLI...")
        email_worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
