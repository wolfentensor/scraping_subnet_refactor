import asyncio
from typing import Any, Tuple
from queue import PriorityQueue
from asyncio import Lock


class AsyncPriorityQueue:
    def __init__(self):
        self._queue = PriorityQueue()
        self._lock = Lock()

    async def put(self, item: Tuple[int, Any]) -> None:
        """
        An async method to put an item into the queue.
        Items must be tuples where the first element is an integer representing the priority.

        Args:
            item (Tuple[int, Any]): The item to put in the queue, with its priority.
        """
        async with self._lock:
            self._queue.put(item)

    async def get(self) -> Any:
        """
        An async method to get an item from the queue.

        Returns:
            The item with the highest priority.
        """
        async with self._lock:
            return self._queue.get()

    async def qsize(self) -> int:
        """
        Returns the number of items in the queue.

        Returns:
            The number of items in the queue.
        """
        async with self._lock:
            return self._queue.qsize()

    async def empty(self) -> bool:
        """
        Check if the queue is empty.

        Returns:
            True if the queue is empty, False otherwise.
        """
        async with self._lock:
            return self._queue.empty()


if __name__ == "__main__":
    # Example usage
    async def main():
        pq = AsyncPriorityQueue()

        # Put some items in the queue
        await pq.put((2, 'item with priority 2'))
        await pq.put((1, 'item with priority 1'))
        await pq.put((3, 'item with priority 3'))

        # Get the items back
        while not await pq.empty():
            item = await pq.get()
            print(f"Got item: {item}")


    asyncio.run(main())
