/*
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
*/
#include "oneflow/core/operator/variable_op.h"
#include "oneflow/core/common/balanced_splitter.h"
#include "oneflow/core/job/sbp_signature_builder.h"

namespace oneflow {

namespace {

Maybe<OptInt64> GetSplitAxis(const VariableOpConf& variable_conf) {
  auto opt_split_axis = std::make_shared<OptInt64>(variable_conf.split_axis());
  if (opt_split_axis->has_value()) {
    size_t num_axes = variable_conf.shape().dim_size();
    if (opt_split_axis->value() < 0) {
      opt_split_axis->set_value(opt_split_axis->value() + num_axes);
    }
    CHECK_GE_OR_RETURN(opt_split_axis->value(), 0);
    CHECK_LT_OR_RETURN(opt_split_axis->value(), num_axes);
  }
  return opt_split_axis;
}

}  // namespace

void VariableOp::InitFromOpConf() {
  CHECK(op_conf().has_variable_conf());
  if (op_conf().variable_conf().has_tick()) { EnrollInputBn("tick", false); }
  bool is_trainable = op_conf().variable_conf().trainable();
  EnrollOutputBn("out", is_trainable)->set_is_mutable(true);
}

Maybe<void> VariableOp::InferLogicalOutBlobDescs(
    const std::function<BlobDesc*(const std::string&)>& BlobDesc4BnInOp,
    const ParallelDesc& parallel_desc) const {
  const VariableOpConf& variable_conf = op_conf().variable_conf();
  BlobDesc* out_blob_desc = BlobDesc4BnInOp("out");
  out_blob_desc->mut_shape() = Shape(variable_conf.shape());
  CHECK_OR_RETURN(variable_conf.has_data_type());
  out_blob_desc->set_data_type(variable_conf.data_type());
  return Maybe<void>::Ok();
}

Maybe<void> VariableOp::InferOutBlobDescs(
    const std::function<BlobDesc*(const std::string&)>& GetBlobDesc4BnInOp,
    const ParallelContext* parallel_ctx) const {
  const VariableOpConf& variable_conf = op_conf().variable_conf();
  BlobDesc* out_blob_desc = GetBlobDesc4BnInOp("out");
  out_blob_desc->mut_shape() = Shape(variable_conf.shape());
  CHECK_OR_RETURN(variable_conf.has_data_type());
  out_blob_desc->set_data_type(variable_conf.data_type());
  if (parallel_ctx->parallel_num() == 1) { return Maybe<void>::Ok(); }
  const Shape& hierarchy = *JUST(GetOpParallelDesc())->hierarchy();
  LOG(INFO) << "variable hierarchy " << hierarchy.DebugStr();
  CHECK_EQ_OR_RETURN(variable_conf.parallel_distribution_size(), hierarchy.NumAxes());
  for (int64_t i = 0; i < hierarchy.NumAxes(); ++i) {
    SbpParallel sbp_parallel;
    CHECK_OR_RETURN(
        ParseSbpParallelFromString(variable_conf.parallel_distribution(i), &sbp_parallel));
    if (sbp_parallel.has_split_parallel()) {
      const int64_t split_axis = sbp_parallel.split_parallel().axis();
      out_blob_desc->mut_shape().Set(split_axis,
                                     out_blob_desc->shape().At(split_axis) / hierarchy.At(i));
    }
  }
  return Maybe<void>::Ok();
}

Maybe<void> VariableOp::GetSbpSignatures(SbpSignatureList* sbp_sig_list) const {
  const auto& opt_split_axis = JUST(GetSplitAxis(op_conf().variable_conf()));
  SbpSignatureBuilder sbp_sig_builder;
  if (opt_split_axis->has_value()) {
    sbp_sig_builder.Split(output_bns(), opt_split_axis->value());
  } else {
    sbp_sig_builder.Broadcast(output_bns());
  }
  sbp_sig_builder.Broadcast(input_bns()).Build(sbp_sig_list->mutable_sbp_signature()->Add());
  return Maybe<void>::Ok();
}

Maybe<void> VariableOp::InferSbpSignature(
    SbpSignature* sbp_signature, const SbpSignature& sbp_sig_conf,
    const std::function<int32_t(const SbpSignature&)>& CalcOrderValue4SbpSig,
    std::function<Maybe<const SbpInferHint*>(const std::string&)> SbpInferHint4Ibn,
    const ParallelDesc& parallel_desc) const {
  SbpSignatureList sbp_sig_list;
  GetSbpSignatures(&sbp_sig_list);
  *sbp_signature = sbp_sig_list.sbp_signature().Get(0);
  return Maybe<void>::Ok();
}

Symbol<OperatorConf> VariableOp::GetOpConfWithoutOpNameAndLbn() const {
  return SymbolOf(this->op_conf());
}

Maybe<void> VariableOp::InferParallelDistributionSignature(
    ParallelDistributionSignature* signature, const SbpSignature& sbp_sig_conf,
    const ParallelDesc& parallel_desc,
    std::function<Maybe<const ParallelDistributionInferHint*>(const std::string&)>
        ParallelDistributionInferHint4Ibn) {
  const auto& parallel_hierarchy = *parallel_desc.hierarchy();
  const VariableOpConf& conf = this->op_conf().variable_conf();
  CHECK_EQ_OR_RETURN(conf.parallel_distribution_size(), parallel_hierarchy.NumAxes());
  ParallelDistribution& out_parallel_distribution =
      (*signature->mutable_bn_in_op2parallel_distribution())["out"];
  for (int64_t i = 0; i < parallel_hierarchy.NumAxes(); ++i) {
    SbpParallel sbp_parallel;
    CHECK_OR_RETURN(ParseSbpParallelFromString(conf.parallel_distribution(i), &sbp_parallel));
    CHECK_OR_RETURN(sbp_parallel.has_split_parallel() || sbp_parallel.has_broadcast_parallel());
    *out_parallel_distribution.mutable_sbp_parallel()->Add() = sbp_parallel;
  }
  if (conf.has_tick()) {
    ParallelDistribution& tick_parallel_distribution =
        (*signature->mutable_bn_in_op2parallel_distribution())["tick"];
    for (int64_t i = 0; i < parallel_hierarchy.NumAxes(); ++i) {
      tick_parallel_distribution.mutable_sbp_parallel()->Add()->mutable_broadcast_parallel();
    }
  }
  return Maybe<void>::Ok();
}

REGISTER_OP(OperatorConf::kVariableConf, VariableOp);
REGISTER_OP_SAME_OUTPUT_BLOB_REGST_NUM(OperatorConf::kVariableConf, 1);
REGISTER_INTERFACE_OP(OperatorConf::kVariableConf);

}  // namespace oneflow
