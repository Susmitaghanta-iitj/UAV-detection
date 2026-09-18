module dense_affine_engine #(
  parameter DIN=32,
  parameter DOUT=8,
  parameter ACC_W=48
)(
  input  logic clk,
  input  logic rst_n,
  input  logic start,

  output logic act_req,
  output logic [$clog2(DIN)-1:0] act_addr,
  input  logic [7:0] act_data,

  output logic wgt_req,
  output logic [$clog2(DIN*DOUT)-1:0] wgt_addr,
  input  logic [7:0] wgt_data,

  output logic out_valid,
  output logic [$clog2(DOUT)-1:0] out_index,
  output logic signed [ACC_W-1:0] out_sum_qaqw,
  output logic signed [ACC_W-1:0] out_sum_qa,

  output logic done
);

  typedef enum logic [2:0] {IDLE,CLEAR,LOAD,MAC,EMIT,NEXT,DONE} state_t;
  state_t st;
  integer i,o;

  logic mac_clear,mac_en;
  logic signed [ACC_W-1:0] sum_qaqw,sum_qa;

  qat_affine_mac_core #(
    .ACT_W(8),.WGT_W(8),.ACC_W(ACC_W)
  ) MAC (
    .clk,.rst_n,.clear(mac_clear),.en(mac_en),
    .act_code(act_data),.wgt_code(wgt_data),
    .sum_qaqw,.sum_qa
  );

  always_comb begin
    act_req=0; wgt_req=0; out_valid=0; done=0;
    mac_clear=0; mac_en=0;
    act_addr=i[$clog2(DIN)-1:0];
    wgt_addr=(o*DIN+i);
    out_index=o[$clog2(DOUT)-1:0];
    out_sum_qaqw=sum_qaqw;
    out_sum_qa=sum_qa;

    case(st)
      CLEAR: mac_clear=1;
      LOAD: begin act_req=1; wgt_req=1; end
      MAC: mac_en=1;
      EMIT: out_valid=1;
      DONE: done=1;
      default: ;
    endcase
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
      st<=IDLE; i<=0; o<=0;
    end else begin
      case(st)
        IDLE: if(start) begin i<=0; o<=0; st<=CLEAR; end
        CLEAR: st<=LOAD;
        LOAD: st<=MAC;
        MAC: begin
          if(i==DIN-1) begin i<=0; st<=EMIT; end
          else begin i<=i+1; st<=LOAD; end
        end
        EMIT: st<=NEXT;
        NEXT: begin
          if(o==DOUT-1) st<=DONE;
          else begin o<=o+1; st<=CLEAR; end
        end
        DONE: st<=IDLE;
        default: st<=IDLE;
      endcase
    end
  end
endmodule
