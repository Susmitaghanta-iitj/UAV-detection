module posit4_1_decode_q16(
 input  logic [3:0] code,
 output logic is_nar,
 output logic signed [31:0] value_q16_16
);
 always_comb begin
   is_nar=1'b0;
   unique case(code)
     4'h0: value_q16_16=32'sd0;
     4'h1: value_q16_16=32'sd4096;
     4'h2: value_q16_16=32'sd16384;
     4'h3: value_q16_16=32'sd32768;
     4'h4: value_q16_16=32'sd65536;
     4'h5: value_q16_16=32'sd131072;
     4'h6: value_q16_16=32'sd262144;
     4'h7: value_q16_16=32'sd1048576;
     4'h8: begin value_q16_16=32'sd0; is_nar=1'b1; end
     4'h9: value_q16_16=-32'sd1048576;
     4'hA: value_q16_16=-32'sd262144;
     4'hB: value_q16_16=-32'sd131072;
     4'hC: value_q16_16=-32'sd65536;
     4'hD: value_q16_16=-32'sd32768;
     4'hE: value_q16_16=-32'sd16384;
     4'hF: value_q16_16=-32'sd4096;
     default: begin value_q16_16=32'sd0; is_nar=1'b1; end
   endcase
 end
endmodule
