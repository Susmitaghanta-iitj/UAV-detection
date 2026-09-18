module conv_pool_latency1_top #(
 parameter CIN=1,COUT=4,LENGTH=32,K=3,POOL=2,AW=16
)(
 input logic clk,rst_n,start,
 input logic signed [31:0] scale_aw_q,scale_al_q,alpha_q,out_scale_q,

 output logic src_req,output logic [AW-1:0] src_addr,
 input logic [7:0] src_data,input logic src_valid,
 output logic wgt_req,output logic [AW-1:0] wgt_addr,
 input logic [7:0] wgt_data,input logic wgt_valid,
 output logic bias_req,output logic [$clog2(COUT)-1:0] bias_addr,
 input logic signed [31:0] bias_data,

 output logic dst_we,output logic [AW-1:0] dst_addr,output logic [7:0] dst_data,
 output logic done
);
 localparam CONVL=((LENGTH+2-K)/1)+1;
 logic conv_start,pool_start,swap,busy,conv_done,pool_done;
 logic conv_we;logic[AW-1:0]conv_waddr;logic[7:0]conv_wdata;
 logic pool_req;logic[AW-1:0]pool_raddr;logic[7:0]pool_rdata;logic pool_rvalid;

 block_latency1_scheduler S(.clk,.rst_n,.start,.conv_done,.pool_done,
  .conv_start,.pool_start,.mem_swap(swap),.busy,.done);

 conv1d_latency1_complete_engine #(.CIN(CIN),.COUT(COUT),.LENGTH(LENGTH),.K(K),.PADDING(1),.AW(AW)) C(
  .clk,.rst_n,.start(conv_start),.scale_aw_q,.scale_al_q,.alpha_q,.out_scale_q,
  .in_req(src_req),.in_addr(src_addr),.in_data(src_data),.in_valid(src_valid),
  .wgt_req,.wgt_addr,.wgt_data,.wgt_valid,.bias_req,.bias_addr,.bias_data,
  .out_we(conv_we),.out_addr(conv_waddr),.out_code(conv_wdata),.done(conv_done));

 sync_read_mem8 #(.DEPTH(COUT*CONVL)) TMP(
  .clk,.we(conv_we),.waddr(conv_waddr),.wdata(conv_wdata),
  .rd_req(pool_req),.rd_addr(pool_raddr),.rd_data(pool_rdata),.rd_valid(pool_rvalid));

 maxpool_latency1_engine #(.CHANNELS(COUT),.LENGTH(CONVL),.POOL(POOL),.AW(AW)) P(
  .clk,.rst_n,.start(pool_start),.in_req(pool_req),.in_addr(pool_raddr),
  .in_data(pool_rdata),.in_valid(pool_rvalid),
  .out_we(dst_we),.out_addr(dst_addr),.out_data(dst_data),.done(pool_done));
endmodule
