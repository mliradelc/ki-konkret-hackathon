import gradio as gr

with gr.Blocks() as demo:
    images = [("images/cat.jpg", "Cat"), ("images/dog.jpg", "Dog"), ("images/cat2.jpg", "Cat too"), ("images/dog2.jpg", "Dog too")]
    table = gr.Dataframe([[1, 2, 3], [4, 5, 6]])
    gallery = gr.Gallery( images,  object_fit="contain", height="auto")
    textbox = gr.Textbox("Hello Cats & Dogs!")
    statement = gr.Textbox()

    def on_select(value, evt: gr.EventData):
        return f"The {evt.target} component was selected, and its value was {value}."

    table.select(on_select, table, statement)
    gallery.select(on_select, gallery, statement)
    textbox.select(on_select, textbox, statement)

demo.launch(server_port=7868, share=True)