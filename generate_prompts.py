import json


def main():

    item = "apple"

    angles = ["", "from top-down view", "from isometric view", "from side view"]
    illumination = ["bright", "dim"]
    light = ["sunlight", "florescent lights"]

    # for each constructed prompt, four images are generated. Increasing this to 2 will generate 8 images per prompt, etc.
    prompt_repeats = 1

    prompts = []
    for angle in angles:
        for light_source in light:
            for light_intensity in illumination:
                for i in range(prompt_repeats):
                    prompts.append(f"realistic image of {item} {angle} with {light_intensity} illumination from {light_source}")

    print(len(prompts), "prompts generated to prompts.json")
    # write prompts to json file
    with open('prompts.json', 'w') as f:
        json.dump(prompts, f)

if __name__ == '__main__':
    main()
