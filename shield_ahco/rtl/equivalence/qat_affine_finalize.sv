module qat_affine_finalize #(
  parameter ACC_W = 48,
  parameter FRAC_W = 24
)(
  input  logic signed [ACC_W-1:0] sum_qaqw,
  input  logic signed [ACC_W-1:0] sum_qa,

  // Fixed-point scale metadata supplied by software:
  // scale_aw = Sa*Sw in Q(FRAC_W)
  // scale_al = Sa*Wlow in Q(FRAC_W)
  // bias_q   = bias in Q(FRAC_W)
  input  logic signed [31:0] scale_aw_q,
  input  logic signed [31:0] scale_al_q,
  input  logic signed [31:0] bias_q,

  output logic signed [63:0] out_q
);
  logic signed [79:0] term0,term1,bias_ext;

  always_comb begin
    term0 = sum_qaqw * scale_aw_q;
    term1 = sum_qa   * scale_al_q;
    bias_ext = {{48{bias_q[31]}},bias_q};
    out_q = term0 + term1 + bias_ext;
  end
endmodule
