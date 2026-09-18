module fxp8_q34_mac #(parameter ACC_W=32)(
 input logic clk,rst_n,clear,en,
 input logic signed [7:0] a_q34,b_q34,
 output logic signed [ACC_W-1:0] acc_q68
);
 logic signed [15:0] product_q68;
 always_comb product_q68 = a_q34 * b_q34;
 always_ff @(posedge clk or negedge rst_n) begin
   if(!rst_n || clear) acc_q68 <= '0;
   else if(en) acc_q68 <= acc_q68 + product_q68;
 end
endmodule
