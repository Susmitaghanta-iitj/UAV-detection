module shared_tp_mac_top #(
 parameter ACC_W=72
)(
 input logic clk,rst_n,clear,en,finalize,
 input logic [1:0] mode,
 input logic [7:0] a_code,b_code,
 output logic valid,
 output logic [7:0] out_code,
 output logic nar_seen,
 output logic signed [ACC_W-1:0] acc_q32_32
);
 logic signed [47:0] rounded_q16_16;

 shared_tp_mac_core #(.ACC_W(ACC_W)) CORE(
   .clk,.rst_n,.clear,.en,.mode,.a_code,.b_code,
   .nar_seen,.acc_q32_32
 );

 always_comb begin
   // one final Q32.32 -> Q16.16 rounding
   if(acc_q32_32 < 0)
     rounded_q16_16 = -(((-acc_q32_32) + (1 <<< 15)) >>> 16);
   else
     rounded_q16_16 = (acc_q32_32 + (1 <<< 15)) >>> 16;
 end

 tp_output_encode ENC(.mode,.nar_seen,.x_q16_16(rounded_q16_16),.out_code);

 always_ff @(posedge clk or negedge rst_n) begin
   if(!rst_n) valid <= 1'b0;
   else valid <= finalize;
 end
endmodule
