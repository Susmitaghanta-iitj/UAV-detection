module qat_affine_pact_finalize #(
  parameter ACC_W = 48,
  parameter CONST_W = 32,
  parameter FRAC_W = 24,
  parameter OUT_W = 8
)(
  input  logic signed [ACC_W-1:0] sum_qaqw,
  input  logic signed [ACC_W-1:0] sum_qa,

  input  logic signed [CONST_W-1:0] scale_aw_q,
  input  logic signed [CONST_W-1:0] scale_al_q,
  input  logic signed [CONST_W-1:0] bias_q,
  input  logic signed [CONST_W-1:0] alpha_q,
  input  logic signed [CONST_W-1:0] out_scale_q,

  output logic signed [79:0] preact_q,
  output logic [OUT_W-1:0] out_code
);

  logic signed [79:0] term0, term1, bias_ext;
  logic signed [79:0] y_q;
  logic signed [79:0] q_round;
  logic signed [79:0] levels;

  always_comb begin
    term0 = sum_qaqw * scale_aw_q;
    term1 = sum_qa   * scale_al_q;
    bias_ext = {{48{bias_q[31]}},bias_q};
    preact_q = term0 + term1 + bias_ext;

    if(preact_q < 0)
      y_q = 0;
    else if(preact_q > alpha_q)
      y_q = alpha_q;
    else
      y_q = preact_q;

    levels = (1 << OUT_W) - 1;

    if(out_scale_q <= 0)
      q_round = 0;
    else
      q_round = (y_q + (out_scale_q >>> 1)) / out_scale_q;

    if(q_round < 0)
      out_code = '0;
    else if(q_round > levels)
      out_code = {OUT_W{1'b1}};
    else
      out_code = q_round[OUT_W-1:0];
  end
endmodule
