module sync_read_mem8 #(
  parameter DEPTH=1024,
  parameter AW=$clog2(DEPTH)
)(
  input  logic clk,
  input  logic we,
  input  logic [AW-1:0] waddr,
  input  logic [7:0] wdata,

  input  logic rd_req,
  input  logic [AW-1:0] rd_addr,
  output logic [7:0] rd_data,
  output logic rd_valid
);
  logic [7:0] mem [0:DEPTH-1];
  logic [AW-1:0] rd_addr_q;
  logic rd_req_q;

  always_ff @(posedge clk) begin
    if(we)
      mem[waddr] <= wdata;

    rd_req_q <= rd_req;
    rd_addr_q <= rd_addr;

    rd_valid <= rd_req_q;
    if(rd_req_q)
      rd_data <= mem[rd_addr_q];
  end
endmodule
