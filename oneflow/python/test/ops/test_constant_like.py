import oneflow as flow
import numpy as np
import os

os.environ['ENABLE_USER_OP'] = 'True'

def _check(test_case, x, y, value, dtype=None):
    np_constant_like = np.full(x.shape, value)
    
    assert np.allclose(np_constant_like, y, rtol=1e-5, atol=1e-5)

def _run_test(test_case, x, value, dtype=None, device='gpu'):
    func_config = flow.FunctionConfig()
    func_config.default_data_type(flow.float)
    func_config.default_distribute_strategy(flow.distribute.consistent_strategy())
    @flow.function(func_config)
    def ConstantLikeJob(x=flow.FixedTensorDef(x.shape)):
        return flow.constant_like(x, value=value, dtype=dtype)
    y = ConstantLikeJob(x).get()
    _check(test_case, x, y.ndarray(), value, dtype=dtype)
   
def test_constant_like_gpu_float(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 1.0, flow.float, 'gpu')
   
def test_constant_like_cpu_float(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 2.0, flow.float, 'cpu')
   
def test_constant_like_gpu_double(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 3.0, flow.double, 'gpu')
   
def test_constant_like_cpu_double(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 4.0, flow.double, 'cpu')
   
def test_constant_like_gpu_int8(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 5.0, flow.int8, 'gpu')
   
def test_constant_like_cpu_int8(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 6.0, flow.int8, 'cpu')

def test_constant_like_gpu_int32(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 7.0, flow.int32, 'gpu')
   
def test_constant_like_cpu_int32(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 8.0, flow.int32, 'cpu')
   
def test_constant_like_gpu_int64(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 9.0, flow.int64, 'gpu')
   
def test_constant_like_cpu_int64(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 10.0, flow.int64, 'cpu')

def test_constant_like_gpu(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 11.0, device='gpu')
   
def test_constant_like_cpu(test_case):
    x = np.random.rand(10, 3, 32, 1024).astype(np.float32)
    _run_test(test_case, x, 12.0, dtype=flow.float, device='cpu')

test_constant_like_gpu(1)