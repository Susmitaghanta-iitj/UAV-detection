module weight_mem #(parameter DEPTH=262144, AW=$clog2(DEPTH))(
 input logic clk,we,input logic [AW-1:0] waddr,input logic [7:0] wdata,
 input logic [AW-1:0] raddr,output logic [7:0] rdata);
 logic [7:0] mem[0:DEPTH-1];
 always_ff @(posedge clk) begin if(we) mem[waddr]<=wdata; rdata<=mem[raddr]; end
endmodule
