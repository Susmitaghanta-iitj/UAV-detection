module posit4_1_mac #(parameter ACC_W=40)(
 input logic clk,rst_n,clear,en,
 input logic [3:0] a_code,b_code,
 output logic nar_seen,
 output logic signed [ACC_W-1:0] acc_q16_16
);
 logic a_nar,b_nar;
 logic signed [15:0] a_q8_8,b_q8_8;
 logic signed [31:0] prod_q16_16;
 posit4_1_decode A(.code(a_code),.is_nar(a_nar),.value_q8_8(a_q8_8));
 posit4_1_decode B(.code(b_code),.is_nar(b_nar),.value_q8_8(b_q8_8));
 always_comb prod_q16_16 = a_q8_8*b_q8_8;
 always_ff @(posedge clk or negedge rst_n) begin
   if(!rst_n || clear) begin acc_q16_16<='0; nar_seen<=1'b0; end
   else if(en) begin
     if(a_nar || b_nar) nar_seen<=1'b1;
     else acc_q16_16 <= acc_q16_16 + prod_q16_16;
   end
 end
endmodule
