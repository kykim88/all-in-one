from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
import asyncio
from consumer import Worker as Consumer

# on_event deprecated -> lifespan으로 변경
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("lifespan start...")
    consumer = Consumer()
    task2 = asyncio.create_task(consumer.process())
    logger.info("lifespan start !")
    yield
    logger.info("lifespan close...")
    task2.cancel()
    if consumer:
        consumer.close()
    logger.info("lifespan closed!")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get_root():
    # logger.debug("this is root!")
    return "this is root"


@app.get("/health")
async def get_health():
    return "healthy"