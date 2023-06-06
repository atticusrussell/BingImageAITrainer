import asyncio
import os
import re
import glob
import json
import sys
from BingImageCreator import ImageGenAsync
from collections import defaultdict


# This will hold successfully processed prompts in an async-io safe manner
processed_prompts = asyncio.Queue()

# A queue to hold cookies and share them among coroutines
cookies_queue = asyncio.Queue()

# A dictionary to hold error counts for each cookie
cookie_errors = defaultdict(int)


class JPEGIndex:
    """
    A class used to manage the indices of JPEG files in a given output directory.
    """

    def __init__(self, output_dir):
        """
        Initializes the JPEGIndex object.

        Args:
            output_dir (str): The directory where JPEG files are stored.
        """
        self.lock = asyncio.Lock()
        self.output_dir = output_dir
        self.jpeg_index = self.get_initial_index()

    def get_initial_index(self):
        """
        Gets the initial index of the JPEG files in the output directory.
        The index is based on the file names and is the maximum index found plus one.
        
        Returns:
            int: The initial index.
        """
        jpeg_files = [f for f in os.listdir(self.output_dir) if f.endswith('.jpeg')]
        jpeg_indices = [int(re.match(r'^(\d+)', f).group(1)) for f in jpeg_files if re.match(r'^(\d+)', f)]
        return max(jpeg_indices, default=-1) + 1

    async def get_next_index(self):
        """
        Gets the next index for a new JPEG file. This is an atomic operation.

        Returns:
            int: The next index.
        """
        async with self.lock:
            next_index = self.jpeg_index
            self.jpeg_index += 1
        return next_index


class PromptIndex:
    """
    A class used to manage the indices of prompts.
    """
    
    def __init__(self):
        """
        Initializes the PromptIndex object.
        """
        self.lock = asyncio.Lock()
        self.prompt_index = 0

    async def get_next_index(self):
        """
        Gets the next index for a new prompt. This is an atomic operation.

        Returns:
            int: The next index.
        """
        async with self.lock:
            next_index = self.prompt_index
            self.prompt_index += 1
        return next_index


async def call_image_gen(prompts_queue, output_dir, coroutine_id, jpeg_index, prompt_index, total_prompts):
    """
    Main task that fetches images for a given prompt and saves them.

    Args:
        prompts_queue (Queue): The queue holding all prompts.
        output_dir (str): The directory to save images.
        coroutine_id (int): The ID of this coroutine.
        jpeg_index (JPEGIndex): An instance of JPEGIndex to get JPEG file indices.
        prompt_index (PromptIndex): An instance of PromptIndex to get prompt indices.
        total_prompts (int): The total number of prompts.
    """
    while not prompts_queue.empty():
        prompt = await prompts_queue.get()
        current_prompt = await prompt_index.get_next_index()  # Update the current prompt counter
        attempts = 0  # Number of attempts made to process the current prompt
        max_attempts = 3  # Maximum number of attempts before giving up on the current prompt

        while attempts < max_attempts:
            # Get a cookie from the queue
            cookie_index, auth_cookie = await cookies_queue.get()
            print(f"\n[CR {coroutine_id}] Using cookie: {cookie_index} for prompt {current_prompt+1} of {total_prompts}")
            try:
                async with ImageGenAsync(auth_cookie=auth_cookie) as image_generator:
                    # Fetch the image links for the given prompt
                    image_links = await image_generator.get_images(prompt)
                    file_index = await jpeg_index.get_next_index()
                    # Create a file_name based on the index of JPEG files in the output directory and the prompt.
                    file_name = f"{str(file_index).zfill(5)}_{prompt.replace(' ', '_')}"
                    # Save the images in the specified directory
                    await image_generator.save_images(image_links, output_dir=output_dir, file_name=file_name)

                    await processed_prompts.put(prompt)
                    # Reset error count for the cookie since it was successful
                    cookie_errors[cookie_index] = 0
                    # Return the cookie back into the queue after use
                    await cookies_queue.put((cookie_index, auth_cookie))
                    break  # Break out of the retry loop if processing was successful

            except KeyError:
                print(f"\n[CR {coroutine_id}] KeyError [Cookie {cookie_index} may have exceeded the daily limit, switching to next cookie.]")
                attempts += 1
                cookie_errors[cookie_index] += 1
                if cookie_errors[cookie_index] < 3:
                    # Return the cookie back into the queue after use if it has not had 3 consecutive errors
                    await cookies_queue.put((cookie_index, auth_cookie))
                else:
                    print(f"\n[CR {coroutine_id}] Cookie {cookie_index} removed after 3 consecutive errors.")

            except Exception as e:
                print(f"\n[CR {coroutine_id}] Error encountered with cookie {cookie_index}, retrying. Attempt {attempts+1} of {max_attempts}.")
                attempts += 1
                cookie_errors[cookie_index] += 1
                if cookie_errors[cookie_index] < 3:
                    # Return the cookie back into the queue after use if it has not had 3 consecutive errors
                    await cookies_queue.put((cookie_index, auth_cookie))
                else:
                    print(f"\n[CR {coroutine_id}] Cookie {cookie_index} removed after 3 consecutive errors.")

        if attempts == max_attempts:
            print(f"\n[CR {coroutine_id}] Failed to process prompt '{prompt}' after {max_attempts} attempts. Skipping to next prompt.")
        prompts_queue.task_done()


def get_cookie_files(directory):
    """
    Returns a list of all cookie files in a given directory.

    Args:
        directory (str): The directory to search for cookie files.

    Returns:
        list: A list of file paths for the found cookie files.
    """
    cookie_files = glob.glob(f'{directory}/bing_cookies_*.json')
    return cookie_files


def read_u_cookies(cookie_files):
    """
    Reads and returns the "_U" cookies from a list of cookie files.

    Args:
        cookie_files (list): A list of cookie file paths.

    Returns:
        list: A list of"_U" cookies.
    """
    u_cookies = []
    for cookie_file in cookie_files:
        with open(cookie_file, 'r') as file:
            cookie_data = json.load(file)
            image_token = [x for x in cookie_data if x.get("name") == "_U"]
            if image_token:
                u_cookies.append(image_token[0].get("value"))
            else:
                print(f"Auth cookie not found in: {cookie_file}")
    return u_cookies


# # Create new function to run tasks
async def run_tasks(tasks):
    """
    Runs a list of tasks concurrently.

    Args:
        tasks (list): A list of tasks to run.
    """
    await asyncio.gather(*tasks)


async def extract_all_from_queue(queue):
    """
    Extracts and returns all items from a queue.

    Args:
        queue (Queue): The queue to extract items from.

    Returns:
        list: A list of items extracted from the queue.
    """
    items = []
    while not queue.empty():
        items.append(await queue.get())
    return items


def main():
    """
    The main function of the script. It initializes necessary classes, 
    reads the prompts and cookies, creates tasks for each cookie, 
    and finally runs the tasks.
    """
    try:
        output_dir = "images"
        # create output directory if it does not exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cookie_dir = "cookies"
        cookie_files = get_cookie_files(cookie_dir)
        
        # if no cookie files are found, exit the program
        if not cookie_files:
            print("No cookie files of the bing_cookies_n.json format found in the 'cookies' directory.")
            sys.exit(1)

        # Read the "_U" cookies from the cookie files
        u_cookies = read_u_cookies(cookie_files)

        # if no cookies were found in the files, exit the program
        if not u_cookies:
            print("No '_U' cookies found in the cookie files.")
            sys.exit(1)

        # Populate the cookies queue with cookies and their indices
        for index, cookie in enumerate(u_cookies):
            cookies_queue.put_nowait((index, cookie))

        with open('prompts.json', 'r') as file:
            prompts = json.load(file)
        
        total_prompts = len(prompts)
        prompt_index = PromptIndex()  # Create an instance of the PromptIndex class

        prompts_queue = asyncio.Queue()
        for prompt in prompts:
            prompts_queue.put_nowait(prompt)

        jpeg_index = JPEGIndex(output_dir)

        tasks = []
        # The number of coroutines is equal to the number of cookies
        for i in range(len(u_cookies)):
            tasks.append(call_image_gen(prompts_queue, output_dir, i, jpeg_index, prompt_index, total_prompts))

        # 'asyncio.run' must be called within an 'async' function
        asyncio.run(run_tasks(tasks))
    
    except Exception as e:
        print(f"Error encountered: {e}")

    finally:
        # After all tasks are done, remove processed prompts from json
        with open('prompts.json', 'r') as file:
            prompts = json.load(file)

        processed_prompts_list = asyncio.run(extract_all_from_queue(processed_prompts))
        remaining_prompts = [prompt for prompt in prompts if prompt not in processed_prompts_list]

        with open('prompts.json', 'w') as file:
            json.dump(remaining_prompts, file)

if __name__ == '__main__':
    main()
