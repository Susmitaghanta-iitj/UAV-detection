module dense_sram_demo_top #(
  parameter DIN=16,
  parameter DOUT=4,
  parameter ACC_W=48
)(
  input logic clk,rst_n,start,
  output logic out_valid,
  output logic [$clog2(DOUT)-1:0] out_index,
  output logic signed [ACC_W-1:0] sum_qaqw,
  output logic signed [ACC_W-1:0] sum_qa,
  output logic done
);

  logic act_req,wgt_req,act_valid,wgt_valid;
  logic [$clog2(DIN)-1:0] act_addr;
  logic [$clog2(DIN*DOUT)-1:0] wgt_addr;
  logic [7:0] act_data,wgt_data;

  sync_read_mem8 #(.DEPTH(DIN)) ACTMEM(
    .clk,
    .we(1'b0),.waddr('0),.wdata('0),
    .rd_req(act_req),.rd_addr(act_addr),
    .rd_data(act_data),.rd_valid(act_valid)
  );

  sync_read_mem8 #(.DEPTH(DIN*DOUT)) WGTMEM(
    .clk,
    .we(1'b0),.waddr('0),.wdata('0),
    .rd_req(wgt_req),.rd_addr(wgt_addr),
    .rd_data(wgt_data),.rd_valid(wgt_valid)
  );

  dense_latency1_engine #(.DIN(DIN),.DOUT(DOUT),.ACC_W(ACC_W)) ENG(
    .clk,.rst_n,.start,
    .act_req,.act_addr,.act_data,.act_valid,
    .wgt_req,.wgt_addr,.wgt_data,.wgt_valid,
    .out_valid,.out_index,.sum_qaqw,.sum_qa,.done
  );
endmodule
