module tp_decode(
 input  logic [1:0] mode,
 input  logic [7:0] code,
 output logic       is_nar,
 output logic signed [31:0] value_q16_16
);
 logic signed [31:0] h21_v,h30_v,p41_v,p82_v;
 logic p41_nar,p82_nar;

 hfp4_e2m1_decode H21(.code(code[3:0]),.value_q16_16(h21_v));
 hfp4_e3m0_decode H30(.code(code[3:0]),.value_q16_16(h30_v));
 posit4_1_decode_q16 P41(.code(code[3:0]),.is_nar(p41_nar),.value_q16_16(p41_v));
 posit8_2_decode P82(.code(code),.is_nar(p82_nar),.value_q16_16(p82_v));

 always_comb begin
   is_nar = 1'b0;
   unique case(mode)
     2'b00: value_q16_16 = h21_v;
     2'b01: value_q16_16 = h30_v;
     2'b10: begin value_q16_16 = p41_v; is_nar=p41_nar; end
     2'b11: begin value_q16_16 = p82_v; is_nar=p82_nar; end
   endcase
 end
endmodule
