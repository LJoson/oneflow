"""
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import absolute_import
from abc import ABC
from typing import Optional

from oneflow.python.framework.function_util import api_oneflow_function
from oneflow.python.oneflow_export import oneflow_export
from oneflow.python.framework.module import Module
from oneflow.python.framework.check_point import CheckPoint
from oneflow.python.ops.optimizer import Optimizer
from oneflow.python.ops.dataloader import DataLoader

@oneflow_export("nn.CheckpointConfig")
class CheckpointConfig(object):
    def __init__(self, load_path, save_path):
        self.load_path = load_path
        self.save_path = save_path


@oneflow_export("nn.Model")
class Model(
    ABC,
    Module,
):
    r"""A high level API for model training and validation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.is_function_style = kwargs['is_function_style']
        self.training_config = kwargs['training_config']
        self.validation_config = kwargs['validation_config']
        self.checkpoint_config = kwargs['checkpoint_config']

        optim_conf = self.configure_optimizers()
        if isinstance(optim_conf, Optimizer):
            self.optimizers = [optim_conf]
        elif isinstance(optim_conf, (list, tuple)):
            self.optimizers = optim_conf
    
        self.train_job = self._lazy_train_job()
        self.eval_job = self._lazy_eval_job()

        self.check_point = CheckPoint()
        if not self.checkpoint_config.load_path:
            self.check_point.init()
        else:
            self.check_point.load(self.checkpoint_config.load_path)


    def forward(self, *args, **kwargs):
        r"""Same as `nn.Module.forward()`, here is to define the operations you want to use for prediction.
        """
        return super().forward(*args, **kwargs)
    
    def training_step(self, *args, **kwargs):
        r"""Operates on a single batch of data from the training set and return loss.
        """
        raise NotImplementedError()

    def validation_step(self, *args, **kwargs):
        r"""Operates on a single batch of data from the validation set.
        """ 
    
    def configure_optimizers(self):
        r"""Choose what optimizers and learning-rate schedulers to use in your optimization.
        Normally you'd need one. But in the case of GANs or similar you might have multiple.
        """
        raise NotImplementedError()
    
    def optimizer_step(
        self,
        epoch: int = None,
        batch_idx: int = None,
        optimizer: Optimizer = None,
        optimizer_idx: int = None
    ) -> None:
        r"""Customized optimizer action.
        """
        # TODO(strint): consider lazy
        optimizer.step()
        optimizer.zero_grad()
    
    def print(self, *args, **kwargs) -> None:
        r"""Only print from root process.
        """
        if self.context.rank == 0:
            print(*args, **kwargs)
    
    def training_data(self):
        raise NotImplementedError

    def validation_data(self):
        raise NotImplementedError

    def _lazy_train_job(self):
        @api_oneflow_function(type="train", function_config=self.training_config)
        def job():
            batch = self.training_data()
            loss = self.training_step(batch, 0)
            self.optimizers[0].minimize(loss)
            return loss
        return job

    def _lazy_eval_job(self):
        @api_oneflow_function(function_config=self.validation_config)
        def eval_job():
            batch = self.validation_data()
            return self.validation_step(batch, 0)
        return eval_job

    def fit(
        self,
        max_epochs: int = 1000,
    ):
        self.max_epochs = max_epochs

        for epoch in range(0, self.max_epochs):
            self.current_epoch = epoch
            print("fit epoch : ", epoch)
            loss = self.train_job().get().mean()
            fmt_str = "{:>12}  {:>12}  {:>12.6f}"
            print(fmt_str.format(epoch, "train loss:", loss))
            if (epoch + 1) % 10 == 0:
                eval_loss = self.eval_job().get().mean()
                print(
                    fmt_str.format(
                        epoch, "eval loss:", eval_loss
                    )
                )
        
        self.check_point.save(self.checkpoint_config.save_path)

    
    def save_checkpoint(
        self,
        filepath,
    ):
        r"""Save model states as a checkpoint.
        """
        pass


    def load_checkpoint(
        self,
        filepath,
    ):
        r"""Load model states from a checkpoint.
        """
        pass