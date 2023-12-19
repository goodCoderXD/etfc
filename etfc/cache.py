import pickle
from datetime import datetime, timedelta
from pathlib import Path
from hashlib import md5


def disk_cache(path: str = ".cache", expiration_time: timedelta = timedelta(weeks=1)):
    """
    A decorator for caching the output of a function to disk.

    Args:
        path (str): The path to the cache directory.
        expiration_time (timedelta): The duration for which the cache is considered valid.

    Returns:
        Callable: The decorated function.
    """
    cache_dir = Path(path)

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache directory if it doesn't exist
            cache_dir.mkdir(exist_ok=True)

            # Generate cache file path based on function name
            hash_input = str(args) + str(kwargs)
            cache_file = (
                cache_dir
                / f"{func.__name__}.{md5(hash_input.encode()).hexdigest()}.pickle"
            )

            if "breakpoint" in func.__code__.co_names:
                print("Rerunning function due to breakpoint()")
            elif (
                # Check if cache is still valid
                cache_file.exists()
                and datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                < expiration_time
            ):
                with open(cache_file, "rb") as file:
                    return pickle.load(file)

            # Cache is expired or doesn't exist, run the function
            result = func(*args, **kwargs)

            # Save result and timestamp to cache file
            with open(cache_file, "wb") as file:
                pickle.dump(result, file)

            return result

        return wrapper

    return decorator


if __name__ == "__main__":

    @disk_cache()
    def example(x, y):
        print("Executing")
        return x + y

    print(example(1, 2))
    print(example(1, 2))
    print(example(1, 3))
