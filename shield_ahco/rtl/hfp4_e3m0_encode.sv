module hfp4_e3m0_encode(
 input logic signed [47:0] x_q16_16,
 output logic [3:0] code
);
 always_comb begin
    if (x_q16_16 <= 48'sd-1048576) code = 4'hF;
    else if (x_q16_16 < 48'sd-786432) code = 4'hF;
    else if (x_q16_16 < 48'sd-393216) code = 4'hE;
    else if (x_q16_16 < 48'sd-196608) code = 4'hD;
    else if (x_q16_16 < 48'sd-98304) code = 4'hC;
    else if (x_q16_16 < 48'sd-49152) code = 4'hB;
    else if (x_q16_16 < 48'sd-24576) code = 4'hA;
    else if (x_q16_16 < 48'sd-8192) code = 4'h9;
    else if (x_q16_16 < 48'sd8192) code = 4'h0;
    else if (x_q16_16 < 48'sd24576) code = 4'h1;
    else if (x_q16_16 < 48'sd49152) code = 4'h2;
    else if (x_q16_16 < 48'sd98304) code = 4'h3;
    else if (x_q16_16 < 48'sd196608) code = 4'h4;
    else if (x_q16_16 < 48'sd393216) code = 4'h5;
    else if (x_q16_16 < 48'sd786432) code = 4'h6;
    else code = 4'h7;
 end
endmodule
