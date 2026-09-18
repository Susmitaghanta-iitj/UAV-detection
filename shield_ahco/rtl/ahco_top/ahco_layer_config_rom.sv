module ahco_layer_config_rom(
 input logic [2:0] layer_id,
 output logic is_conv,
 output logic is_dense,
 output logic [15:0] cin_din,
 output logic [15:0] cout_dout,
 output logic [15:0] length,
 output logic [7:0] kernel,
 output logic [7:0] pool
);
 always_comb begin
  is_conv=0;is_dense=0;cin_din=0;cout_dout=0;length=0;kernel=0;pool=0;
  case(layer_id)
   3'd0:begin is_conv=1;cin_din=1; cout_dout=16; length=35280;kernel=64;pool=8;end
   3'd1:begin is_conv=1;cin_din=16;cout_dout=32; length=4410; kernel=32;pool=8;end
   3'd2:begin is_conv=1;cin_din=32;cout_dout=64; length=551;  kernel=16;pool=4;end
   3'd3:begin is_conv=1;cin_din=64;cout_dout=256;length=137;  kernel=4; pool=0;end
   // Report-aligned reduced dense path: 8,704 -> 128 -> 64 -> 2
   3'd4:begin is_dense=1;cin_din=8704;cout_dout=128;end
   3'd5:begin is_dense=1;cin_din=128; cout_dout=64;end
   3'd6:begin is_dense=1;cin_din=64;  cout_dout=2;end
   default:;
  endcase
 end
endmodule
