module qat_affine_mac_core #(
  parameter ACT_W = 8,
  parameter WGT_W = 8,
  parameter ACC_W = 48
)(
  input  logic                    clk,
  input  logic                    rst_n,
  input  logic                    clear,
  input  logic                    en,
  input  logic [ACT_W-1:0]        act_code,
  input  logic [WGT_W-1:0]        wgt_code,
  output logic signed [ACC_W-1:0] sum_qaqw,
  output logic signed [ACC_W-1:0] sum_qa
);
  logic [ACT_W+WGT_W-1:0] prod;

  always_comb prod = act_code * wgt_code;

  always_ff @(posedge clk or negedge rst_n) begin
    if(!rst_n || clear) begin
      sum_qaqw <= '0;
      sum_qa   <= '0;
    end else if(en) begin
      sum_qaqw <= sum_qaqw + $signed({1'b0,prod});
      sum_qa   <= sum_qa   + $signed({1'b0,act_code});
    end
  end
endmodule
