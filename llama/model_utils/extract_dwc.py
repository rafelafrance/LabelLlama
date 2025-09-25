import argparse
import json

import dspy
from rich.console import Console

from llama.data_formats import label_types
from llama.model_utils.model_utils import release_gpu_memory_ollama
from llama.pylib import darwin_core as dwc
from llama.pylib import log


def extract_info(args: argparse.Namespace) -> None:
    log.started(args=args)

    label_type = label_types.LABEL_TYPES[args.label_type]

    console = Console(log_path=False)

    lm = dspy.LM(args.model, api_base=args.api_base, api_key=args.api_key, cache=False)
    dspy.configure(lm=lm)

    label_data = label_types.read_label_data(args.label_json)
    limit = args.limit if args.limit else len(label_data)
    label_data = label_data[:limit]

    extractor = dspy.Predict(label_type.signature)

    predictions = []

    for i, label in enumerate(label_data, 1):
        console.log(f"[blue]{i} {'=' * 80}")
        console.log(f"[blue]{label['path']}")
        console.log(f"[blue]{label['text']}")

        pred = extractor(text=label["text"], prompt=label_type.prompt)

        console.log(f"[green]{pred}")

        as_dict = {
            "path": label["path"],
            "text": label["text"],
            "annotations": dwc.to_dwc_keys(pred.toDict(), label_type.dwc),
        }

        predictions.append(as_dict)

    with args.annotations_json.open("w") as f:
        f.write(json.dumps(predictions, indent=4) + "\n")

    release_gpu_memory_ollama(args.model)

    log.finished()
