module ping_pong_feature_mem #(
  parameter DEPTH=65536,
  parameter AW=$clog2(DEPTH)
)(
  input logic clk,
  input logic swap,

  input logic src_we,
  input logic [AW-1:0] src_waddr,
  input logic [7:0] src_wdata,
  input logic [AW-1:0] src_raddr,
  output logic [7:0] src_rdata,

  input logic dst_we,
  input logic [AW-1:0] dst_waddr,
  input logic [7:0] dst_wdata,
  input logic [AW-1:0] dst_raddr,
  output logic [7:0] dst_rdata,

  output logic src_is_a
);
  logic [7:0] mem_a[0:DEPTH-1];
  logic [7:0] mem_b[0:DEPTH-1];

  always_ff @(posedge clk) begin
    if(swap) src_is_a <= ~src_is_a;

    if(src_we) begin
      if(src_is_a) mem_a[src_waddr] <= src_wdata;
      else         mem_b[src_waddr] <= src_wdata;
    end

    if(dst_we) begin
      if(src_is_a) mem_b[dst_waddr] <= dst_wdata;
      else         mem_a[dst_waddr] <= dst_wdata;
    end

    if(src_is_a) begin
      src_rdata <= mem_a[src_raddr];
      dst_rdata <= mem_b[dst_raddr];
    end else begin
      src_rdata <= mem_b[src_raddr];
      dst_rdata <= mem_a[dst_raddr];
    end
  end

  initial src_is_a = 1'b1;
endmodule
