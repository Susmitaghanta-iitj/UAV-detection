module shared_tp_mac_core #(
 parameter ACC_W = 72
)(
 input  logic                   clk,
 input  logic                   rst_n,
 input  logic                   clear,
 input  logic                   en,
 input  logic [1:0]             mode,
 input  logic [7:0]             a_code,
 input  logic [7:0]             b_code,
 output logic                   nar_seen,
 output logic signed [ACC_W-1:0] acc_q32_32
);
 logic a_nar,b_nar;
 logic signed [31:0] a_q16_16,b_q16_16;
 logic signed [63:0] prod_q32_32;

 tp_decode DA(.mode(mode),.code(a_code),.is_nar(a_nar),.value_q16_16(a_q16_16));
 tp_decode DB(.mode(mode),.code(b_code),.is_nar(b_nar),.value_q16_16(b_q16_16));

 always_comb prod_q32_32 = a_q16_16 * b_q16_16;

 always_ff @(posedge clk or negedge rst_n) begin
   if(!rst_n || clear) begin
     acc_q32_32 <= '0;
     nar_seen <= 1'b0;
   end else if(en) begin
     if(a_nar || b_nar)
       nar_seen <= 1'b1;
     else
       acc_q32_32 <= acc_q32_32 + prod_q32_32;
   end
 end
endmodule
