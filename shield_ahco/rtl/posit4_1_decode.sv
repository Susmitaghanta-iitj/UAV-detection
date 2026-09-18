module posit4_1_decode(
 input logic [3:0] code,
 output logic is_nar,
 output logic signed [15:0] value_q8_8
);
 always_comb begin
   is_nar=1'b0;
   case(code)
     4'h0: value_q8_8=16'sd0;
     4'h1: value_q8_8=16'sd16;
     4'h2: value_q8_8=16'sd64;
     4'h3: value_q8_8=16'sd128;
     4'h4: value_q8_8=16'sd256;
     4'h5: value_q8_8=16'sd512;
     4'h6: value_q8_8=16'sd1024;
     4'h7: value_q8_8=16'sd4096;
     4'h8: begin value_q8_8=16'sd0; is_nar=1'b1; end
     4'h9: value_q8_8=-16'sd4096;
     4'hA: value_q8_8=-16'sd1024;
     4'hB: value_q8_8=-16'sd512;
     4'hC: value_q8_8=-16'sd256;
     4'hD: value_q8_8=-16'sd128;
     4'hE: value_q8_8=-16'sd64;
     4'hF: value_q8_8=-16'sd16;
   endcase
 end
endmodule
