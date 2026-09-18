from __future__ import annotations
import argparse
from .model_1dfcnn import ModelConfig, Shield1DFCNN

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-length", type=int, required=True)
    args = ap.parse_args()
    model = Shield1DFCNN(args.input_length, ModelConfig())
    print(model)
    print("flatten_dim =", model.flatten_dim)
    print("source pre-pruning target flatten_dim = 35072")
    print("source post-pruning target flatten_dim = 8704")

if __name__ == "__main__":
    main()
