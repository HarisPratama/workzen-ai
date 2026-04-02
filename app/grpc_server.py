import logging
import os
import grpc
from concurrent import futures
from grpc_health.v1 import health, health_pb2_grpc, health_pb2
import app.ai_pb2 as pb2
import app.ai_pb2_grpc as pb2_grpc
from app.ai import analyze_cv, match_cv_with_jd
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AIServiceServicer(pb2_grpc.AIServiceServicer):
    def AnalyzeCV(self, request, context):
        if not request.cv_text or not request.cv_text.strip():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("cv_text is required and cannot be empty")
            return pb2.CVAnalysisResponse()

        logger.info(f"gRPC AnalyzeCV called with text length: {len(request.cv_text)}")
        try:
            result = analyze_cv(request.cv_text)
            return pb2.CVAnalysisResponse(
                summary=result.summary,
                recommendation=result.recommendation,
                skills=result.skills,
                experience_highlights=result.experience_highlights,
                fit_score=result.fit_score
            )
        except Exception as e:
            logger.error(f"Error in AnalyzeCV: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"AI Analysis failed: {str(e)}")
            return pb2.CVAnalysisResponse()

    def MatchJob(self, request, context):
        if not request.cv_text or not request.cv_text.strip():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("cv_text is required and cannot be empty")
            return pb2.JobMatchResponse()
        if not request.jd_text or not request.jd_text.strip():
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("jd_text is required and cannot be empty")
            return pb2.JobMatchResponse()

        logger.info(f"gRPC MatchJob called with CV length: {len(request.cv_text)} and JD length: {len(request.jd_text)}")
        try:
            result = match_cv_with_jd(request.cv_text, request.jd_text)
            return pb2.JobMatchResponse(
                score=result.score,
                matched_skills=result.matched_skills,
                missing_skills=result.missing_skills,
                explanation=result.explanation,
                verdict=result.verdict
            )
        except Exception as e:
            logger.error(f"Error in MatchJob: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Matching failed: {str(e)}")
            return pb2.JobMatchResponse()


def create_grpc_server():
    port = os.getenv("GRPC_PORT", "50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=40))

    # Register AI service
    pb2_grpc.add_AIServiceServicer_to_server(AIServiceServicer(), server)

    # Register health check service
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("ai.AIService", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)

    server.add_insecure_port(f'[::]:{port}')
    logger.info(f"gRPC Server started on port {port}")
    server.start()
    return server


def serve_grpc():
    server = create_grpc_server()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve_grpc()
