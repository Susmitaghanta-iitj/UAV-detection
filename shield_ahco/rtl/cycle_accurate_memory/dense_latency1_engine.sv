module dense_latency1_engine #(
  parameter DIN=16,
  parameter DOUT=4,
  parameter ACC_W=48
)(
  input logic clk,
  input logic rst_n,
  input logic start,

  output logic act_req,
  output logic [$clog2(DIN)-1:0] act_addr,
  input logic [7:0] act_data,
  input logic act_valid,

  output logic wgt_req,
  output logic [$clog2(DIN*DOUT)-1:0] wgt_addr,
  input logic [7:0] wgt_data,
  input logic wgt_valid,

  output logic out_valid,
  output logic [$clog2(DOUT)-1:0] out_index,
  output logic signed [ACC_W-1:0] sum_qaqw,
  output logic signed [ACC_W-1:0] sum_qa,
  output logic done
);

  typedef enum logic [2:0] {IDLE,CLEAR,ISSUE,WAIT,CONSUME,EMIT,DONE} st_t;
  st_t st;

  integer i,o;
  logic signed [ACC_W-1:0] acc_prod, acc_qa;

  always_comb begin
    act_req=0; wgt_req=0; out_valid=0; done=0;
    act_addr=i;
    wgt_addr=o*DIN+i;
    out_index=o;
    sum_qaqw=acc_prod;
    sum_qa=acc_qa;

    case(st)
      ISSUE: begin act_req=1; wgt_req=1; end
      EMIT: out_valid=1;
      DONE: done=1;
      default: ;
    endcase
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
      st<=IDLE; i<=0; o<=0; acc_prod<='0; acc_qa<='0;
    end else begin
      case(st)
        IDLE: if(start) begin i<=0; o<=0; st<=CLEAR; end
        CLEAR: begin
          acc_prod<='0; acc_qa<='0; st<=ISSUE;
        end
        ISSUE: st<=WAIT;
        WAIT: if(act_valid && wgt_valid) st<=CONSUME;
        CONSUME: begin
          acc_prod <= acc_prod + act_data*wgt_data;
          acc_qa   <= acc_qa   + act_data;
          if(i==DIN-1) begin
            i<=0; st<=EMIT;
          end else begin
            i<=i+1; st<=ISSUE;
          end
        end
        EMIT: begin
          if(o==DOUT-1) st<=DONE;
          else begin o<=o+1; st<=CLEAR; end
        end
        DONE: st<=IDLE;
        default: st<=IDLE;
      endcase
    end
  end
endmodule
