import csv
import openai
from gingerit.gingerit import GingerIt
import os
import pandas

# Specify data sources
PI_data = 'PI_data.csv'
baseline_database = 'baseline_database.csv'


def read_key():
    with open('key.txt') as file:
        key = file.read()
    return key


def send_prompt_davinci(prompt, key):
    openai.api_key = key
    model_engine = "text-davinci-003"
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5
    )

    response = completion.choices[0].text
    # print("\nPrompt to OpenAI server: " + prompt)
    print(response)


def send_prompt_gpt35turbo_ref(conversation, key):
    import openai

    openai.api_key = key
    model_id = 'gpt-3.5-turbo'

    def ChatGPT_conversation(conversation):
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=conversation
        )
        # api_usage = response['usage']
        # print('Total token consumed: {0}'.format(api_usage['total_tokens']))
        # stop means complete
        # print(response['choices'][0].finish_reason)
        # print(response['choices'][0].index)
        conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
        return conversation

    conversation = []
    conversation.append({'role': 'system', 'content': 'How may I help you?'})
    conversation = ChatGPT_conversation(conversation)
    print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))

    while True:
        prompt = input('User:')
        conversation.append({'role': 'user', 'content': prompt})
        conversation = ChatGPT_conversation(conversation)
        print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))


def send_prompt_gpt35turbo(prompt, key):
    # import openai

    openai.api_key = key
    model_id = 'gpt-3.5-turbo'

    def ChatGPT_conversation(conversation):
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=conversation
        )
        # api_usage = response['usage']
        # print('Total token consumed: {0}'.format(api_usage['total_tokens']))
        # stop means complete
        # print(response['choices'][0].finish_reason)
        # print(response['choices'][0].index)
        conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
        return conversation

    conversation = []
    conversation.append({'role': 'system', 'content': prompt})
    conversation = ChatGPT_conversation(conversation)
    print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), conversation[-1]['content'].strip()))


def extract_equipment():
    with open(PI_data) as file:
        input_data = csv.DictReader(file)  # Read PI data
        equipment_list = []

        # Generate list of equipment
        for row in input_data:
            equipment = row['equipment']
            if equipment not in equipment_list:
                equipment_list.append(equipment)

    return equipment_list


def generate_abnormalities_sentence(abnormality_list, abnormality_count, prompt):
    if abnormality_count == 1:  # If only 1 issue detected
        prompt = prompt + ' ' + abnormality_list[0]
    elif abnormality_count == 2:  # If 2 issues detected
        prompt = prompt + ' ' + abnormality_list[0] + ' and ' + abnormality_list[1]
    else:  # If more than 2 issues detected
        for issues in abnormality_list:
            if issues == abnormality_list[-1]:  # When reached the end of the list
                prompt = prompt + ' and ' + issues
            elif issues == abnormality_list[0]:  # For the first issue in the list
                prompt = prompt + ' ' + issues
            else:
                prompt = prompt + ', ' + issues

    return prompt


# Input actual data for an equipment and output result whether the actual data is high, low or normal
def determine_attribute_status(equipment, attribute, actual_data):
    # set default attribute status as normal
    attribute_status = 'normal'

    with open(baseline_database) as file:
        database = csv.DictReader(file)  # Generate dictionary from csv file
        for row in database:
            if equipment == row['equipment'] and attribute == row['attribute']:
                if actual_data < int(row['baseline_min']):
                    attribute_status = 'low'
                elif actual_data > int(row['baseline_max']):
                    attribute_status = 'high'
        return attribute_status


def grammar_correction(prompt):
    parser = GingerIt()
    return parser.parse(prompt)


def generate_single_prompt(equipment):
    # initialize abnormality count to 0
    abnormality_count = 0

    with open(PI_data) as file:
        input_data = csv.DictReader(file)  # Read PI data
        abnormality_list = []
        # equipment_list = extract_equipment()

        # Initialize prompt
        prompt = f'List possible causes and solutions for power plant {equipment} experiencing'

        for row in input_data:

            attribute = row['attribute']
            actual_data = int(row['actual_data'])

            status = determine_attribute_status(equipment, attribute, actual_data)

            if status != 'normal':
                abnormality_list.append(f'{status} {attribute}')
                abnormality_count = abnormality_count + 1

        # combine initialized prompt with discovered issue(s)
        return generate_abnormalities_sentence(abnormality_list, abnormality_count, prompt)


def generate_multi_prompt():
    prompt_list = []
    equipment_list = extract_equipment();
    # print(equipment_list)

    for equipment in equipment_list:
        prompt = generate_single_prompt(equipment)
        prompt_list.append(prompt)

    return prompt_list
