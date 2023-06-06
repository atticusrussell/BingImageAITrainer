# Bing Image AI Trainer
### A tool for generating diverse synthetic training images using Bing Image Creator to facilitate the training of AI vision models.
#
Getting training data for AI models involving imaging is difficult. I created this tool to generate synthetic training images while changing as many or as few parameters about the images as desired. This is accomplished using Bing Image Creator, which uses the DALLE-2 model.

Prompts are generated using `generate_prompts.py`, which supports creating as many or as few prompts as you need, and varying none or many parameters. Then, the tool, `generate_images.py` automatically generates images from the generated prompts, leveraging the incredible [acheong08's Bing Image Creator API](https://github.com/acheong08/BingImageCreator), and saves the results in `images`.

The user must supply their own cookie files for Bing Image Creator, which I explain [here](#getting-cookies), but the program will concurrently use as many cookies as are available to it in the `cookies` folder in order to dramatically speed up image generation.


## Setup

1. If you don’t already have Python installed, install it now. You can [find it here](https://www.python.org/downloads/).

2. Clone this repository.

3. Navigate into the project directory:

   ```bash
   cd bingimageaitrainer
   ```

4. Create a new virtual environment:

   ```bash
   python -m venv venv
   . venv/bin/activate
   ```

5. Install the requirements:

   ```bash
   pip install -r requirements.txt
   ```

### Getting Cookies

1. Open a web browser like Chrome, Firefox, or Edge

2. Log into a Microsoft account
-  NOTE: A Microsoft account can only create one unique cookie that will work for this, and the cookie from any given MS account is limited to a certain number of images per day.

3. Open [bing.com/images/create](https://www.bing.com/images/create)

4. If you see a "Join & Create" button, click it. If not, and you can use Bing Image Creator, you're already good to continue.

5. Install the cookie editor extension for [Chrome](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) or [Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)

6. Go to [bing.com](https://bing.com)

7. Open the extension

8. Click "Export" on the bottom right, then "Export as JSON" (This saves your cookies to clipboard)

9. Paste your cookies into a file `bing_cookies_*.json` in the `cookies` directory, where `*` indicates that what comes between `cookies_` and  `.json` is irrelevant to the program. I suggest giving each cookie a number to keep track of it though.

## Running the code

1. Modify `generate_prompts.py` based on what parameters you want to vary in the generated images, what you want images of, and how many images you want from each prompt. By default, four images are generated from every prompt to Bing Image Creator. You may need to tweak the prompt system significantly to consistently generate suitable images for your application.

2. Populate `prompts.json` by running 
```bash 
python3 generate_prompts.py
```

3. Make sure that you have at least one Bing Image Creator cookie file in json format in the `cookies` directory

4. Generate images with 
```bash
python3 bic_generate.py
```

5. If the code crashes before images are generated for all prompts, run 
```bash
python3 bic_generate.py
```
 again. Don't worry; the generated images are tracked through removal from `prompts.json`, so duplicate images will not be generated.


## Legal Notice <a name="legal-notice"></a>

This repository is _not_ associated with or endorsed by providers of the websites, services, and APIs contained in this GitHub repository. This project is intended **for educational purposes only**. This is just a little personal project. 

Please note the following:

1. **Disclaimer**: The websites, APIs, services, and trademarks mentioned in this repository belong to their respective owners. This project is _not_ claiming any right over them nor is it affiliated with or endorsed by any of the providers mentioned.

2. **Responsibility**: The author of this repository is _not_ responsible for any consequences, damages, or losses arising from the use or misuse of this repository or the content provided by the third-party websites and APIs. Users are solely responsible for their actions and any repercussions that may follow. We strongly recommend the users to follow the TOS of the each Website.

3. **Educational Purposes Only**: This repository and its content are provided strictly for educational purposes. By using the information and code provided, users acknowledge that they are using the websites, APIs and models at their own risk and agree to comply with any applicable laws and regulations.

4. **Indemnification**: Users agree to indemnify, defend, and hold harmless the author of this repository from and against any and all claims, liabilities, damages, losses, or expenses, including legal fees and costs, arising out of or in any way connected with their use or misuse of this repository, its content, third-party websites, or related third-party APIs.

5. **Updates and Changes**: The author reserves the right to modify, update, or remove any content, information, or features in this repository at any time without prior notice. Users are responsible for regularly reviewing the content and any changes made to this repository.

By using this repository or any code related to it, you agree to these terms. The author is not responsible for any copies, forks, or reuploads made by other users. To prevent impersonation or irresponsible actions, you may comply with the MIT license this Repository uses.


