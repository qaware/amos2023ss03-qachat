from InstructorEmbedding import INSTRUCTOR

# load the model
model = INSTRUCTOR('hkunlp/instructor-large', device='cpu')  # you can use GPU

# Inference
sentence = "3D ActionSLAM: wearable person tracking in multi-floor environments"
instruction = "Represent the Science title:"

embeddings = model.encode([[instruction, sentence]])
# you can also normalize the embeddings:  normalize_embeddings=True

print(f"Quantized Embeddings:\n {embeddings}")