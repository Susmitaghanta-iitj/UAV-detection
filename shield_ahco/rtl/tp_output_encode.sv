module tp_output_encode(
 input  logic [1:0] mode,
 input  logic       nar_seen,
 input  logic signed [47:0] x_q16_16,
 output logic [7:0] out_code
);
 logic [3:0] h21,h30,p41;
 logic [7:0] p82;

 hfp4_e2m1_encode E21(.x_q16_16(x_q16_16),.code(h21));
 hfp4_e3m0_encode E30(.x_q16_16(x_q16_16),.code(h30));
 posit4_1_encode EP4(.x_q16_16(x_q16_16),.code(p41));
 posit8_2_encode EP8(.x_q16_16(x_q16_16),.code(p82));

 always_comb begin
   unique case(mode)
     2'b00: out_code = {4'b0,h21};
     2'b01: out_code = {4'b0,h30};
     2'b10: out_code = nar_seen ? 8'h08 : {4'b0,p41};
     2'b11: out_code = nar_seen ? 8'h80 : p82;
   endcase
 end
endmodule
