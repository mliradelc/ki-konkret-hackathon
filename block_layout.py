import gradio as gr

def greet(name_string, year_string):
    return {output_name: name_string, output_year: year_string}

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1, min_width=300):
            name = gr.Textbox(label="Name")
        with gr.Column(scale=1, min_width=300):
            birth_year = gr.Textbox(label="Birth year")
    with gr.Row():
        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                output_name = gr.Textbox(label="Output Name")
            with gr.Column(scale=1, min_width=300):
                output_year = gr.Textbox(label="Output Year")

    with gr.Row():
        greet_btn = gr.Button("GO!")
        greet_btn.click(
            fn=greet,
            inputs=[name, birth_year],
            outputs=[output_name, output_year]
        )

demo.launch(server_port=7867, share=True)
