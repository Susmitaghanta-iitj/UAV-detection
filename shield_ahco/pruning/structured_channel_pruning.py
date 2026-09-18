from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import copy
import torch
from torch import nn


@dataclass
class PruneDecision:
    layer_name: str
    original_channels: int
    kept_channels: int
    keep_indices: list[int]


def l1_channel_importance(conv: nn.Conv1d) -> torch.Tensor:
    """
    Clean-room channel-importance metric:
      importance_j = mean(|W_j|)
    where W_j is output channel j.

    The thesis specifies structured channel pruning, but does not publish
    the exact channel-importance metric. L1 magnitude is therefore used
    as a reproducible baseline, not claimed as the author's exact method.
    """
    return conv.weight.detach().abs().mean(dim=(1, 2))


def select_keep_indices(conv: nn.Conv1d, keep_ratio: float) -> torch.Tensor:
    scores = l1_channel_importance(conv)
    k = max(1, int(round(conv.out_channels * keep_ratio)))
    _, idx = torch.topk(scores, k=k, largest=True, sorted=True)
    return torch.sort(idx).values


def _copy_bn(src: nn.BatchNorm1d, keep: torch.Tensor) -> nn.BatchNorm1d:
    dst = nn.BatchNorm1d(len(keep))
    with torch.no_grad():
        dst.weight.copy_(src.weight[keep])
        dst.bias.copy_(src.bias[keep])
        dst.running_mean.copy_(src.running_mean[keep])
        dst.running_var.copy_(src.running_var[keep])
    return dst


def prune_sequential_conv_blocks(model: nn.Module, keep_ratios: list[float]):
    """
    Physically rebuild Conv1d/BatchNorm1d channel dimensions for the
    thesis-style sequential Conv blocks.

    Assumes each feature block contains:
      Conv1d -> optional BatchNorm1d -> ReLU -> optional Pool
    """
    pruned = copy.deepcopy(model)
    blocks = pruned.features
    if len(keep_ratios) != len(blocks):
        raise ValueError("Need one keep ratio per convolution block")

    prev_keep = None
    decisions: list[PruneDecision] = []

    for bi, (block, ratio) in enumerate(zip(blocks, keep_ratios)):
        seq = block.block
        conv_idx = next(i for i,m in enumerate(seq) if isinstance(m, nn.Conv1d))
        conv = seq[conv_idx]
        keep = select_keep_indices(conv, ratio)

        in_idx = prev_keep
        new_in = conv.in_channels if in_idx is None else len(in_idx)
        new_conv = nn.Conv1d(
            new_in, len(keep),
            kernel_size=conv.kernel_size,
            stride=conv.stride,
            padding=conv.padding,
            dilation=conv.dilation,
            groups=1,
            bias=conv.bias is not None,
            padding_mode=conv.padding_mode,
        )

        with torch.no_grad():
            w = conv.weight[keep]
            if in_idx is not None:
                w = w[:, in_idx, :]
            new_conv.weight.copy_(w)
            if conv.bias is not None:
                new_conv.bias.copy_(conv.bias[keep])

        seq[conv_idx] = new_conv

        for i,m in enumerate(seq):
            if isinstance(m, nn.BatchNorm1d):
                seq[i] = _copy_bn(m, keep)
                break

        decisions.append(
            PruneDecision(
                layer_name=f"features.{bi}.conv",
                original_channels=conv.out_channels,
                kept_channels=len(keep),
                keep_indices=keep.cpu().tolist(),
            )
        )
        prev_keep = keep

    return pruned, decisions


def count_conv_macs(model: nn.Module, input_length: int) -> int:
    """
    Exact Conv1d MAC count using a dry-run forward hook.
    """
    macs = 0
    hooks = []

    def hook(m: nn.Conv1d, inp, out):
        nonlocal macs
        # out: [N, Cout, Lout]
        lout = out.shape[-1]
        macs += (
            lout
            * m.out_channels
            * (m.in_channels // m.groups)
            * m.kernel_size[0]
        )

    for m in model.modules():
        if isinstance(m, nn.Conv1d):
            hooks.append(m.register_forward_hook(hook))

    with torch.no_grad():
        model.features(torch.zeros(1, 1, input_length))

    for h in hooks:
        h.remove()
    return int(macs)


def dense_macs(model: nn.Module) -> int:
    total = 0
    for m in model.classifier.modules():
        if isinstance(m, nn.Linear):
            total += m.in_features * m.out_features
    return total
