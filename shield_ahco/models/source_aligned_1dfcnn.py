import torch
from torch import nn
from .architecture_profiles import THESIS_BASELINE

class SameConvBlock(nn.Module):
    def __init__(self,c_in,stage,profile):
        super().__init__()
        ops=[nn.Conv1d(c_in,stage.out_channels,stage.kernel_size,padding="same")]
        if profile.batch_norm: ops.append(nn.BatchNorm1d(stage.out_channels))
        ops.append(nn.ReLU(inplace=True))
        if stage.pool_size: ops.append(nn.MaxPool1d(stage.pool_size,stride=stage.pool_size))
        if profile.conv_dropout is not None: ops.append(nn.Dropout(profile.conv_dropout))
        self.block=nn.Sequential(*ops)
    def forward(self,x): return self.block(x)

class SourceAligned1DFCNN(nn.Module):
    def __init__(self,profile=THESIS_BASELINE,input_length=None,post_pruning=False,reconcile_pruning_claim=True):
        super().__init__()
        self.profile=profile
        self.input_length=input_length or profile.input_length
        if self.input_length is None: raise ValueError("input_length required")
        blocks=[]; c=1
        for s in profile.conv_stages:
            blocks.append(SameConvBlock(c,s,profile)); c=s.out_channels
        self.features=nn.Sequential(*blocks)
        self.extra_pool=None
        if post_pruning:
            p=4 if reconcile_pruning_claim else 8
            self.extra_pool=nn.MaxPool1d(p,stride=p)
        with torch.no_grad():
            z=self.features(torch.zeros(1,1,self.input_length))
            self.pre_extra_shape=tuple(z.shape)
            self.pre_extra_flatten=int(z.numel())
            if self.extra_pool is not None: z=self.extra_pool(z)
            self.feature_shape=tuple(z.shape)
            self.flatten_dim=int(z.numel())
        dense=[]; d=self.flatten_dim
        for width in profile.dense_dims:
            dense += [nn.Linear(d,width),nn.ReLU(inplace=True),nn.Dropout(profile.dense_dropout)]
            d=width
        dense.append(nn.Linear(d,profile.output_classes))
        self.classifier=nn.Sequential(*dense)
    def forward(self,x):
        x=self.features(x)
        if self.extra_pool is not None: x=self.extra_pool(x)
        return self.classifier(torch.flatten(x,1))

def make_thesis_baseline(post_pruning=False,reconcile_pruning_claim=True):
    return SourceAligned1DFCNN(THESIS_BASELINE,post_pruning=post_pruning,reconcile_pruning_claim=reconcile_pruning_claim)
