module hfp4_e2m1_encode(
 input logic signed [47:0] x_q16_16,
 output logic [3:0] code
);
 always_comb begin
    if (x_q16_16 <= 48'sd-393216) code = 4'hF;
    else if (x_q16_16 < 48'sd-327680) code = 4'hF;
    else if (x_q16_16 < 48'sd-229376) code = 4'hE;
    else if (x_q16_16 < 48'sd-163840) code = 4'hD;
    else if (x_q16_16 < 48'sd-114688) code = 4'hC;
    else if (x_q16_16 < 48'sd-81920) code = 4'hB;
    else if (x_q16_16 < 48'sd-57344) code = 4'hA;
    else if (x_q16_16 < 48'sd-24576) code = 4'h9;
    else if (x_q16_16 < 48'sd24576) code = 4'h0;
    else if (x_q16_16 < 48'sd57344) code = 4'h1;
    else if (x_q16_16 < 48'sd81920) code = 4'h2;
    else if (x_q16_16 < 48'sd114688) code = 4'h3;
    else if (x_q16_16 < 48'sd163840) code = 4'h4;
    else if (x_q16_16 < 48'sd229376) code = 4'h5;
    else if (x_q16_16 < 48'sd327680) code = 4'h6;
    else code = 4'h7;
 end
endmodule
