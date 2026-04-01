import grpc
from concurrent import futures
import proto.ai_service_pb2 as pb2
import proto.ai_service_pb2_grpc as pb2_grpc
from app.ai import analyze_cv, match_cv_with_jd

class AIServiceServicer(pb2_grpc.AIServiceServicer):
    def AnalyzeCV(self, request, context):
        print(f"gRPC AnalyzeCV called with text length: {len(request.cv_text)}")
        try:
            result = analyze_cv(request.cv_text)
            return pb2.AnalyzeResponse(
                summary=result.summary,
                recommendation=result.recommendation,
                skills=result.skills,
                experience_highlights=result.experience_highlights,
                fit_score=result.fit_score
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"AI Analysis failed: {str(e)}")
            return pb2.AnalyzeResponse()

    def MatchCV(self, request, context):
        print(f"gRPC MatchCV called with CV length: {len(request.cv_text)} and JD length: {len(request.jd_text)}")
        try:
            result = match_cv_with_jd(request.cv_text, request.jd_text)
            return pb2.MatchResponse(
                score=result.score,
                matched_skills=result.matched_skills,
                missing_skills=result.missing_skills,
                explanation=result.explanation,
                verdict=result.verdict
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Matching failed: {str(e)}")
            return pb2.MatchResponse()

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_AIServiceServicer_to_server(AIServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC Server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve_grpc()
