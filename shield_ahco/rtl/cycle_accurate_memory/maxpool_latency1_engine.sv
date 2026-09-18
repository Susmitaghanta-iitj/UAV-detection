module maxpool_latency1_engine #(
  parameter CHANNELS=4,
  parameter LENGTH=32,
  parameter POOL=2,
  parameter AW=16
)(
  input logic clk,rst_n,start,

  output logic in_req,
  output logic [AW-1:0] in_addr,
  input logic [7:0] in_data,
  input logic in_valid,

  output logic out_we,
  output logic [AW-1:0] out_addr,
  output logic [7:0] out_data,
  output logic done
);

  localparam OUTL=LENGTH/POOL;
  typedef enum logic[2:0] {IDLE,ISSUE,WAIT,CONSUME,WRITE,ADV,DONE} st_t;
  st_t st;
  integer c,ox,k;
  logic [7:0] best;

  always_comb begin
    in_req=0; out_we=0; done=0;
    in_addr=c*LENGTH+ox*POOL+k;
    out_addr=c*OUTL+ox;
    out_data=best;

    case(st)
      ISSUE: in_req=1;
      WRITE: out_we=1;
      DONE: done=1;
      default: ;
    endcase
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
      st<=IDLE; c<=0; ox<=0; k<=0; best<=0;
    end else begin
      case(st)
        IDLE: if(start) begin c<=0;ox<=0;k<=0;best<=0;st<=ISSUE; end
        ISSUE: st<=WAIT;
        WAIT: if(in_valid) st<=CONSUME;
        CONSUME: begin
          if(k==0 || in_data>best) best<=in_data;
          if(k==POOL-1) begin
            k<=0; st<=WRITE;
          end else begin
            k<=k+1; st<=ISSUE;
          end
        end
        WRITE: st<=ADV;
        ADV: begin
          if(ox==OUTL-1) begin
            ox<=0;
            if(c==CHANNELS-1) st<=DONE;
            else begin c<=c+1;best<=0;st<=ISSUE; end
          end else begin
            ox<=ox+1;best<=0;st<=ISSUE;
          end
        end
        DONE: st<=IDLE;
        default: st<=IDLE;
      endcase
    end
  end
endmodule
