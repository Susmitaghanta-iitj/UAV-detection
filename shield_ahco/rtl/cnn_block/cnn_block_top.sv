module cnn_block_top #(
  parameter CIN=1,
  parameter COUT=4,
  parameter LENGTH=32,
  parameter K=3,
  parameter POOL=2,
  parameter MEM_DEPTH=65536,
  parameter AW=$clog2(MEM_DEPTH)
)(
  input logic clk,rst_n,start,

  // Externally-provided quantization metadata and weight/bias memories
  input logic signed [31:0] scale_aw_q,scale_al_q,alpha_q,out_scale_q,

  output logic weight_req,
  output logic [AW-1:0] weight_addr,
  input logic [7:0] weight_data,

  output logic bias_req,
  output logic [$clog2(COUT)-1:0] bias_addr,
  input logic signed [31:0] bias_data,

  output logic done
);
  // CNN-block integration architectural shell:
  // source feature SRAM -> complete Conv1D engine -> temporary conv buffer
  // -> maxpool -> destination feature SRAM -> ping-pong swap.
  //
  // Exact memory-latency timing remains intentionally explicit for co-verification
  // rather than hidden behind combinational memory assumptions.

  logic conv_start,pool_start,mem_swap,busy;
  logic conv_done,pool_done;

  cnn_block_scheduler S(
    .clk,.rst_n,.start,.conv_done,.pool_done,
    .conv_start,.pool_start,.mem_swap,.busy,.done
  );

  // Datapath instances are integrated in the next stage after memory-latency
  // handshakes are made cycle-accurate.
  assign conv_done = 1'b0;
  assign pool_done = 1'b0;
  assign weight_req = 1'b0;
  assign weight_addr = '0;
  assign bias_req = 1'b0;
  assign bias_addr = '0;
endmodule
