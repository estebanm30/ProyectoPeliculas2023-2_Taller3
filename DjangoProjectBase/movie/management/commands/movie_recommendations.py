from openai.embeddings_utils import get_embedding, cosine_similarity
import numpy as np

#Generar binario
desc = "película de la segunda guerra mundial"
emb = get_embedding(desc,engine='text-embedding-ada-002')

#Recuperar lista a partir del archivo binario
emb_binary = np.array(emb).tobytes()
rec_emb = list(np.frombuffer(emb_binary, dtype=arr.dtype))