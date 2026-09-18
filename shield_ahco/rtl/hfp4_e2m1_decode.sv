module hfp4_e2m1_decode(input logic [3:0] code, output logic signed [31:0] value_q16_16);
  always_comb begin
    unique case(code)
      4'h0: value_q16_16 = 32'sd0;
      4'h1: value_q16_16 = 32'sd49152;
      4'h2: value_q16_16 = 32'sd65536;
      4'h3: value_q16_16 = 32'sd98304;
      4'h4: value_q16_16 = 32'sd131072;
      4'h5: value_q16_16 = 32'sd196608;
      4'h6: value_q16_16 = 32'sd262144;
      4'h7: value_q16_16 = 32'sd393216;
      4'h8: value_q16_16 = 32'sd0;
      4'h9: value_q16_16 = 32'sd-49152;
      4'hA: value_q16_16 = 32'sd-65536;
      4'hB: value_q16_16 = 32'sd-98304;
      4'hC: value_q16_16 = 32'sd-131072;
      4'hD: value_q16_16 = 32'sd-196608;
      4'hE: value_q16_16 = 32'sd-262144;
      4'hF: value_q16_16 = 32'sd-393216;
      default: value_q16_16 = 32'sd0;
    endcase
  end
endmodule
