import openai
import pandas as pd
import glob
import os

# Load your OpenAI API key
openai.api_key = "Add Your API Key Here"


class FoodAssistant:
    def __init__(self, file_path):
        self.food_data = self.load_food_data(file_path)
        self.greetings = ["hi", "hello", "hey"]
        self.thanks = ["thank you", "thanks"]
        self.messages = [{"role": "system", "content": f"Provide information based on Food Data: {self.food_data}"}]

    def load_food_data(self, file_path):
        try:
            csv_file_names = [os.path.basename(file) for file in glob.glob(os.path.join(file_path, '*.csv'))]
            df = pd.read_csv(str(file_path)+str(csv_file_names[0]))
            # Convert the DataFrame to a dictionary
            food_data = df.to_dict(orient='list')
            return food_data
        except Exception as e:
            print(e)
            food_data = {"No Food Data Available"}
            return food_data

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def process_user_input(self, user_input):
        # Check if the user input contains a greeting or thanks
        for greeting in self.greetings:
            if greeting in user_input.lower():
                return f"Hello! How can I assist you today?"

        for thank in self.thanks:
            if thank in user_input.lower():
                return f"You're welcome! If you have any more questions, feel free to ask."

        self.add_message("user", f"Answer the query based on provided Food Data \n Query : {user_input}")

        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages
        )

        reply = chat.choices[0].message.content
        self.add_message("assistant", reply)
        print(self.messages)
        return reply
