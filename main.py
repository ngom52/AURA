import openai
import os
import AURA_functions

key = AURA_functions.read_key()
print(key)

# Solution for SSL Certificate Error caused by Zscaler VPN
os.environ['REQUESTS_CA_BUNDLE'] = 'Zscaler Root CA.crt'

prompt_list = AURA_functions.generate_multi_prompt()

for prompt in prompt_list:
    print(prompt)
    # AURA_functions.send_prompt_gpt35turbo(prompt, key)
    # AURA_functions.send_prompt_davinci(prompt, key)

# prompt = prompt_list[1]
# corrected_prompt = AURA_functions.grammar_correction(prompt)
# print(corrected_prompt['result'])
# AURA_functions.send_prompt_gpt35turbo(prompt, key)
# AURA_functions.send_prompt_davinci(prompt, key)
